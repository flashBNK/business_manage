from datetime import UTC, datetime, timedelta
from uuid import UUID

from domain.member.exceptions import MembersNotFound
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.registration_saga.models import CreateRegistrationSagaDTO
from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from usecases.registration.compensate.implementation import PostgreSQLCompensateRegistrationUseCase


class PostgreSQLRegistrationSagaUseCase:
    def __init__(self, uow: PostgreSQLAuthUnitOfWork):
        self._uow = uow

    async def tasks_completed(self, saga_id: UUID, correlation_id: UUID, causation_id: UUID) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get(saga_id=saga_id)

        if saga is None:
            return

        if saga.correlation_id != correlation_id or saga.status != RegistrationStatus.ORG_COMPLETED:
            return

        member = await uow.member.get_by_invite_id(invite_id=saga.invite_id)
        if member is None:
            raise MembersNotFound

        user = await uow.user.get(user_id=saga.user_id)

        await uow.member.activation_shift(member_id=member.id, flag=True)

        await uow.registration_saga.update_status(
            saga_id=saga.id,
            status=RegistrationStatus.COMPLETED,
            deadline_at=None,
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_COMPLETED,
                aggregate_id=saga.id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "saga_id": str(saga.id),
                    "user_id": str(saga.user_id),
                    "company_id": str(saga.company_id),
                },
            )
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.EMPLOYEE_ACTIVATED,
                aggregate_id=saga.user_id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "user_id": str(saga.user_id),
                    "company_id": str(saga.company_id),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_active": True,
                },
            )
        )

    async def start(self, payload: dict, correlation_id: UUID, causation_id: UUID) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get_by_correlation_id(correlation_id=correlation_id)

        if saga is not None:
            return

        saga = await uow.registration_saga.create(
            CreateRegistrationSagaDTO(
                user_id=UUID(payload["user_id"]),
                company_id=UUID(payload["company_id"]),
                invite_id=UUID(payload["invite_id"]),
                correlation_id=correlation_id,
                deadline_at=datetime.now(UTC) + timedelta(minutes=1),
            )
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_ORG_PROVISION,
                aggregate_id=saga.id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "saga_id": str(saga.id),
                    "user_id": payload["user_id"],
                    "company_id": payload["company_id"],
                    "invite_id": payload["invite_id"],
                    "struct_adm_id": payload["struct_adm_id"],
                    "position_id": payload["position_id"],
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                },
            )
        )

    async def org_completed(self, saga_id: UUID, correlation_id: UUID, causation_id: UUID, payload: dict) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get(saga_id=saga_id)

        if saga is None:
            return

        if saga.correlation_id != correlation_id or saga.status != RegistrationStatus.STARTED:
            return

        await uow.registration_saga.update_status(
            saga_id=saga.id,
            status=RegistrationStatus.ORG_COMPLETED,
            deadline_at=datetime.now(UTC) + timedelta(minutes=1),
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_TASKS_PROVISION,
                aggregate_id=saga.id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "saga_id": str(saga.id),
                    "user_id": str(saga.user_id),
                    "company_id": str(saga.company_id),
                    "invite_id": str(saga.invite_id),
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                    "struct_adm_id": payload["struct_adm_id"],
                    "position_id": payload["position_id"],
                },
            )
        )

    async def tasks_failed(self, saga_id: UUID, correlation_id: UUID, causation_id: UUID, payload: dict) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get(saga_id=saga_id)

        if saga is None:
            return

        if saga.correlation_id != correlation_id or saga.status != RegistrationStatus.ORG_COMPLETED:
            return

        await uow.registration_saga.update_status(
            saga_id=saga.id,
            status=RegistrationStatus.COMPENSATING,
            deadline_at=datetime.now(UTC) + timedelta(minutes=1),
            last_error=payload.get("reason") or "tasks step failed",
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_ORG_COMPENSATE,
                aggregate_id=saga.id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "saga_id": str(saga.id),
                    "user_id": str(saga.user_id),
                    "company_id": str(saga.company_id),
                    "struct_adm_id": payload["struct_adm_id"],
                    "position_id": payload["position_id"],
                },
            )
        )

    async def org_compensated(self, saga_id: UUID, correlation_id: UUID, causation_id: UUID) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get(saga_id=saga_id)

        if saga is None:
            return

        if saga.correlation_id != correlation_id or saga.status != RegistrationStatus.COMPENSATING:
            return

        await PostgreSQLCompensateRegistrationUseCase(uow=uow).execute(
            saga=saga,
            reason=saga.last_error or "tasks step failed",
            causation_id=causation_id,
        )

    async def org_failed(self, saga_id: UUID, correlation_id: UUID, causation_id: UUID, payload: dict) -> None:
        uow = self._uow
        saga = await uow.registration_saga.get(saga_id=saga_id)

        if saga is None:
            return

        if saga.correlation_id != correlation_id or saga.status != RegistrationStatus.STARTED:
            return

        await PostgreSQLCompensateRegistrationUseCase(uow=uow).execute(
            saga=saga,
            reason=payload.get("reason") or "org step failed",
            causation_id=causation_id,
        )
