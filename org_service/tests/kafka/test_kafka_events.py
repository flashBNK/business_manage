import uuid
from datetime import UTC, datetime

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import (
    CompanyReplica,
    StructAdm,
    UsersReplica,
)
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select

from ..fixtures.factories import make_event


async def create_company(session, company_id: uuid.UUID | None = None, name: str = "Test Company") -> CompanyReplica:
    company = CompanyReplica(id=company_id or uuid.uuid4(), name=name)

    session.add(company)
    await session.commit()

    return company


async def create_user(
    session,
    user_id: uuid.UUID | None = None,
    company_id: uuid.UUID | None = None,
    is_active: bool = True,
) -> UsersReplica:
    user = UsersReplica(
        id=user_id or uuid.uuid4(),
        company_id=company_id or uuid.uuid4(),
        username="test_user",
        is_active=is_active,
        last_event_at=datetime.now(UTC),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest.mark.asyncio
async def test_create_company_and_root_structure(session):
    company_id = uuid.uuid4()

    event = make_event(
        event_type="company.created",
        aggregate_id=company_id,
        payload={"company_id": str(company_id), "name": "Test Company"},
    )

    uow = PostgreSQLOrgUnitOfWork(session)

    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    company = await session.scalar(select(CompanyReplica).where(CompanyReplica.id == company_id))

    assert company is not None
    assert company.name == "Test Company"

    root = await session.scalar(select(StructAdm).where(StructAdm.company_id == company_id))

    assert root is not None
    assert root.path is not None
    assert str(root.path) == f"c{company_id.hex}"
