from datetime import UTC, datetime
from uuid import uuid4

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.task import Task
from infrastructure.databases.postgresql.models.task_assignees import TaskAssignees
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from sqlalchemy import select

from ..fixtures.factories import make_event


@pytest.mark.asyncio
async def test_registration_tasks_provision_creates_welcome_task(session):
    user_id = uuid4()
    company_id = uuid4()
    saga_id = uuid4()
    event_id = uuid4()
    correlation_id = uuid4()

    event_data = make_event(
        event_type="registration.tasks.provision",
        aggregate_id=user_id,
        correlation_id=correlation_id,
        payload={
            "saga_id": str(saga_id),
            "user_id": str(user_id),
            "company_id": str(company_id),
            "invite_id": str(uuid4()),
            "struct_adm_id": str(uuid4()),
            "position_id": str(uuid4()),
            "first_name": "Ivan",
            "last_name": "Ivanov",
        },
    )

    event_data["event_id"] = str(event_id)
    event_data["occurred_at"] = datetime.now(UTC).isoformat()

    event = EventEnvelopeDTO.from_dict(event_data)

    async with PostgreSQLTasksUnitOfWork(session=session) as uow:
        from infrastructure.kafka.consumer.handlers import handle_registration_tasks_provision

        await handle_registration_tasks_provision(event=event, uow=uow)

    task = await session.scalar(
        select(Task).where(
            Task.title == "Welcome!",
            Task.author_id == user_id,
            Task.company_id == company_id,
        )
    )
    assert task is not None
    assert task.description == "Initialization."
    assert task.estimated_minutes == 30
    assert task.status.value == "todo"

    assignee = await session.scalar(
        select(TaskAssignees).where(
            TaskAssignees.task_id == task.id,
            TaskAssignees.user_id == user_id,
        )
    )
    assert assignee is not None

    created_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.aggregate_id == task.id,
            OutboxEvent.event_type == "task.created",
        )
    )
    assert created_event is not None
    assert created_event.correlation_id == correlation_id
    assert created_event.causation_id == event_id

    completed_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.aggregate_id == saga_id,
            OutboxEvent.event_type == "registration.tasks.completed",
        )
    )
    assert completed_event is not None
    assert completed_event.correlation_id == correlation_id
    assert completed_event.causation_id == event_id
    assert completed_event.payload["saga_id"] == str(saga_id)
    assert completed_event.payload["user_id"] == str(user_id)
    assert completed_event.payload["company_id"] == str(company_id)
