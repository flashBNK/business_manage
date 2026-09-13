from uuid import UUID

from domain.kafka.models import EventEnvelopeDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.registration_saga.models import CreateRegistrationSagaDTO, RegistrationSagaDTO
from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork

CONSUMER_NAME = "auth_service"


async def handle_employee_registered(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    payload = event.payload

    saga = await uow.registration_saga.get_by_correlation_id(correlation_id=event.correlation_id)

    if saga is not None:
        return

    saga = await uow.registration_saga.create(
        CreateRegistrationSagaDTO(
            user_id=UUID(payload["user_id"]),
            company_id=UUID(payload["company_id"]),
            invite_id=UUID(payload["invite_id"]),
            correlation_id=event.correlation_id,
        )
    )

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_ORG_PROVISION,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
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


async def handle_org_completed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.STARTED:
        return

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.ORG_COMPLETED)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_TASKS_PROVISION,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
            payload={
                "saga_id": str(saga.id),
                "user_id": str(saga.user_id),
                "company_id": str(saga.company_id),
                "invite_id": str(saga.invite_id),
                "first_name": event.payload["first_name"],
                "last_name": event.payload["last_name"],
                "struct_adm_id": event.payload["struct_adm_id"],
                "position_id": event.payload["position_id"],
            },
        )
    )


async def handle_tasks_completed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.ORG_COMPLETED:
        return

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.TASKS_COMPLETED)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_COMPLETED,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
            payload={
                "saga_id": str(saga.id),
                "user_id": str(saga.user_id),
                "company_id": str(saga.company_id),
            },
        )
    )


async def handle_registration_completed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.TASKS_COMPLETED:
        return

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.COMPLETED)


async def handle_tasks_failed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.ORG_COMPLETED:
        return

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.COMPENSATING)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_ORG_COMPENSATE,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
            payload={
                "saga_id": str(saga.id),
                "user_id": str(saga.user_id),
                "company_id": str(saga.company_id),
                "struct_adm_id": event.payload["struct_adm_id"],
                "position_id": event.payload["position_id"],
            },
        )
    )


async def handle_org_compensated(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.COMPENSATING:
        return

    await compensate_auth(uow=uow, saga=saga)

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.FAILED)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_FAILED,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
            payload={
                "saga_id": str(saga.id),
                "reason": "tasks step failed; compensation completed",
            },
        )
    )


async def handle_org_failed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    saga = await uow.registration_saga.get(saga_id=event.aggregate_id)

    if saga is None:
        return

    if saga.correlation_id != event.correlation_id or saga.status != RegistrationStatus.STARTED:
        return

    await compensate_auth(uow=uow, saga=saga)

    await uow.registration_saga.update_status(saga_id=saga.id, status=RegistrationStatus.FAILED)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_FAILED,
            aggregate_id=saga.id,
            correlation_id=saga.correlation_id,
            causation_id=event.event_id,
            payload={"saga_id": str(saga.id), "reason": event.payload.get("reason", "org step failed")},
        )
    )


async def compensate_auth(uow: PostgreSQLAuthUnitOfWork, saga: RegistrationSagaDTO) -> None:
    invite = await uow.invite.get(invite_id=saga.invite_id)
    account_id = invite.account_id if invite else None
    await uow.user.delete(user_id=saga.user_id)

    if account_id is not None:
        await uow.account.delete(account_id=account_id)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.EMPLOYEE_REGISTRATION_FAILED,
            aggregate_id=saga.user_id,
            correlation_id=saga.correlation_id,
            payload={
                "user_id": str(saga.user_id),
                "company_id": str(saga.company_id),
                "reason": "registration failed",
            },
        )
    )


async def handle_employee_created(event, uow) -> None:
    return


async def handle_registration_failed(event, uow) -> None:
    return


async def handle_employee_registration_failed(event, uow) -> None:
    return


EVENT_HANDLERS = {
    "employee.registered": handle_employee_registered,
    "employee.created": handle_employee_created,
    "registration.org.completed": handle_org_completed,
    "registration.org.failed": handle_org_failed,
    "registration.tasks.completed": handle_tasks_completed,
    "registration.tasks.failed": handle_tasks_failed,
    "registration.org.compensated": handle_org_compensated,
    "registration.completed": handle_registration_completed,
    "registration.failed": handle_registration_failed,
    "employee.registration.failed": handle_employee_registration_failed,
}
