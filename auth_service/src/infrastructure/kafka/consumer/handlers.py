from domain.kafka.models import EventEnvelopeDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from usecases.registration.saga.implementation import PostgreSQLRegistrationSagaUseCase


async def handle_employee_registered(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.start(
        payload=event.payload,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
    )


async def handle_org_completed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.org_completed(
        saga_id=event.aggregate_id,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
        payload=event.payload,
    )


async def handle_tasks_completed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.tasks_completed(
        saga_id=event.aggregate_id,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
    )


async def handle_tasks_failed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.tasks_failed(
        saga_id=event.aggregate_id,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
        payload=event.payload,
    )


async def handle_org_compensated(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.org_compensated(
        saga_id=event.aggregate_id,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
    )


async def handle_org_failed(event: EventEnvelopeDTO, uow: PostgreSQLAuthUnitOfWork) -> None:
    usecase = PostgreSQLRegistrationSagaUseCase(uow=uow)

    await usecase.org_failed(
        saga_id=event.aggregate_id,
        correlation_id=event.correlation_id,
        causation_id=event.event_id,
        payload=event.payload,
    )


async def handle_registration_completed(event, uow) -> None:
    return


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
