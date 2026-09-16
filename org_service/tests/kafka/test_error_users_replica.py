import uuid

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import UsersReplica
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select

from ..fixtures.factories import make_event
from ..kafka.test_kafka_events import create_company, create_user


@pytest.mark.asyncio
async def test_employee_registration_failed_deletes_users_replica(session):
    company_id = uuid.uuid4()
    user_id = uuid.uuid4()

    await create_company(session, company_id=company_id)

    await create_user(session, user_id=user_id, company_id=company_id)

    assert await session.scalar(select(UsersReplica).where(UsersReplica.id == user_id)) is not None

    event = make_event(
        event_type="employee.registration.failed",
        aggregate_id=user_id,
        payload={"user_id": str(user_id), "company_id": str(company_id)},
    )

    uow = PostgreSQLOrgUnitOfWork(session)

    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    user = await session.scalar(select(UsersReplica).where(UsersReplica.id == user_id))

    assert user is None
