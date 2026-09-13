from datetime import UTC, datetime, timedelta
from uuid import UUID

from domain.kafka.models import EventEnvelopeDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.exceptions import ParticipantInactive, ParticipantNotFound, ParticipantWrongCompany
from domain.task.models import CreateTaskDTO
from domain.task.participants import validate_participant
from domain.task_assignees.models import CreateTaskAssigneesDTO
from domain.users_replica.models import CreateUsersReplicaDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

log = get_logger(__name__)


async def handle_employee_upsert(event: EventEnvelopeDTO, uow: PostgreSQLTasksUnitOfWork) -> None:
    payload = event.payload
    dto = CreateUsersReplicaDTO(
        id=UUID(payload["user_id"]),
        username=payload["first_name"] + " " + payload["last_name"],
        company_id=UUID(payload["company_id"]),
        is_active=payload["is_active"],
        last_event_at=event.occurred_at,
    )
    log.info("user dto", dto=dto)
    await uow.users_replica.upsert(dto=dto)

    log.info("user successfully added to the database", payload=payload)


async def handle_registration_tasks_provision(event: EventEnvelopeDTO, uow: PostgreSQLTasksUnitOfWork) -> None:
    payload = event.payload

    saga_id = UUID(payload["saga_id"])
    user_id = UUID(payload["user_id"])
    company_id = UUID(payload["company_id"])

    user_replica = CreateUsersReplicaDTO(
        id=user_id,
        username=f"{payload['first_name']} {payload['last_name']}",
        company_id=company_id,
        is_active=True,
        last_event_at=event.occurred_at,
    )

    await uow.users_replica.upsert(dto=user_replica)

    try:
        await validate_participant(
            author_id=user_id,
            responsible_id=user_id,
            company_id=company_id,
            watcher_ids=[],
            assignee_ids=[user_id],
            uow=uow,
        )

        task_dto = CreateTaskDTO(
            title="Welcome!",
            description="Initialization.",
            deadline=datetime.now(UTC) + timedelta(days=7),
            responsible_id=user_id,
            author_id=user_id,
            company_id=company_id,
            estimated_minutes=30,
            watcher_ids=[],
            assignee_ids=[user_id],
        )

        task = await uow.task.create(dto=task_dto)

        await uow.task_assignees.create(dto=CreateTaskAssigneesDTO(task_id=task.id, user_id=user_id))

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.TASK_CREATED,
                aggregate_id=task.id,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
                payload={
                    "title": task.title,
                    "description": task.description,
                    "author_id": str(task.author_id),
                    "responsible_id": str(task.responsible_id),
                    "company_id": str(task.company_id),
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "status": task.status,
                    "estimated_minutes": task.estimated_minutes,
                    "assignee_ids": [str(user_id)],
                    "watcher_ids": [],
                },
            )
        )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_TASKS_COMPLETED,
                aggregate_id=saga_id,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
                payload={
                    "saga_id": str(saga_id),
                    "user_id": str(user_id),
                    "company_id": str(company_id),
                    "invite_id": payload["invite_id"],
                    "struct_adm_id": payload["struct_adm_id"],
                    "position_id": payload["position_id"],
                },
            )
        )

    except (ParticipantNotFound, ParticipantInactive, ParticipantWrongCompany) as exc:
        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_TASKS_FAILED,
                aggregate_id=saga_id,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
                payload={
                    "saga_id": str(saga_id),
                    "user_id": str(user_id),
                    "company_id": str(company_id),
                    "invite_id": payload["invite_id"],
                    "struct_adm_id": payload["struct_adm_id"],
                    "position_id": payload["position_id"],
                    "reason": str(exc),
                },
            )
        )


async def handle_employee_registration_failed(event: EventEnvelopeDTO, uow: PostgreSQLTasksUnitOfWork) -> None:
    user_id = UUID(event.payload["user_id"])
    await uow.users_replica.delete(users_replica_id=user_id)


EVENT_HANDLERS = {
    "employee.created": handle_employee_upsert,
    "employee.registered": handle_employee_upsert,
    "registration.tasks.provision": handle_registration_tasks_provision,
    "employee.registration.failed": handle_employee_registration_failed,
}
