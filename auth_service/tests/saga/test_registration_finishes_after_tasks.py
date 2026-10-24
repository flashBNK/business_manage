from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.members import Members
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.kafka.consumer.handlers import handle_tasks_completed
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy import select

from .conftest import create_employee, make_event


@pytest.mark.asyncio
async def test_registration_finishes_after_tasks_completed(client, session, admin):
    employee = await create_employee(client, session, admin, uuid4(), uuid4())
    response = await client.post(
        "/api/v1/employees/invite-complete",
        json={"invite_token": employee["invite"].code, "password": employee["password"]},
    )
    assert response.status_code == 201

    saga = RegistrationSaga(
        user_id=employee["user_id"],
        company_id=admin["company_id"],
        invite_id=employee["invite"].id,
        correlation_id=uuid4(),
        status=RegistrationStatus.ORG_COMPLETED,
        deadline_at=datetime.now(UTC) + timedelta(minutes=1),
    )
    session.add(saga)
    await session.commit()
    saga_id = saga.id
    event = EventEnvelopeDTO.from_dict(
        make_event("registration.tasks.completed", saga_id, saga.correlation_id, {})
    )

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_tasks_completed(event=event, uow=uow)

    saga = await session.get(RegistrationSaga, saga_id)
    member = await session.scalar(select(Members).where(Members.invite_id == saga.invite_id))
    events = (
        await session.scalars(select(OutboxEvent).where(OutboxEvent.correlation_id == event.correlation_id))
    ).all()

    assert saga.status == RegistrationStatus.COMPLETED
    assert saga.deadline_at is None
    assert member.is_active is True
    assert sorted(saved.event_type for saved in events) == ["employee.activated", "registration.completed"]
    assert all(saved.causation_id == event.event_id for saved in events)
