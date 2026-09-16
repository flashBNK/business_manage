import uuid

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import UsersReplica
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select

from ..fixtures.factories import make_event
from ..kafka.test_kafka_events import create_company


@pytest.mark.asyncio
async def test_create_users_replica(session):
    company_id = uuid.uuid4()
    user_id = uuid.uuid4()

    await create_company(session, company_id=company_id)

    event = make_event(
        event_type="employee.created",
        aggregate_id=user_id,
        payload={
            "user_id": str(user_id),
            "company_id": str(company_id),
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "name": "Ivan",
            "is_active": True,
        },
    )

    uow = PostgreSQLOrgUnitOfWork(session)

    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    user = await session.scalar(select(UsersReplica).where(UsersReplica.id == user_id))

    assert user is not None
    assert user.company_id == company_id
    assert user.username == "Ivan Ivanov"
    assert user.is_active is True

    assert user.last_event_at is not None
