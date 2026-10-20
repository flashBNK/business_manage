from uuid import UUID

from domain.invite.models import UpdateInviteDTO
from domain.member.exceptions import MembersNotFound
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.registration_saga.models import RegistrationSagaDTO
from infrastructure.databases.postgresql.models.invite import InviteStatus
from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork

from .abstract import AbstractCompensateRegistrationUseCase


class PostgreSQLCompensateRegistrationUseCase(AbstractCompensateRegistrationUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork):
        self._uow = uow

    async def execute(self, saga: RegistrationSagaDTO, reason: str, causation_id: UUID) -> None:
        uow = self._uow

        saga = await uow.registration_saga.get(saga_id=saga.id)

        if saga is None or saga.status not in (
            RegistrationStatus.STARTED,
            RegistrationStatus.COMPENSATING,
        ):
            return

        member = await uow.member.get_by_invite_id(invite_id=saga.invite_id)
        if member is None:
            raise MembersNotFound

        await uow.invite.update(invite_id=saga.invite_id, dto=UpdateInviteDTO(status=InviteStatus.REVOKED))

        await uow.member.activation_shift(member_id=member.id, flag=False)

        await uow.registration_saga.update_status(
            saga_id=saga.id, status=RegistrationStatus.FAILED, deadline_at=None, last_error=reason
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.EMPLOYEE_REGISTRATION_FAILED,
                aggregate_id=saga.user_id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "user_id": str(saga.user_id),
                    "company_id": str(saga.company_id),
                    "reason": reason,
                },
            )
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_FAILED,
                aggregate_id=saga.id,
                correlation_id=saga.correlation_id,
                causation_id=causation_id,
                payload={
                    "saga_id": str(saga.id),
                    "reason": reason,
                },
            )
        )
