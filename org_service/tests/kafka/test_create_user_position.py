import uuid

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import (
    OutboxEvent,
    Position,
    StructAdm,
    StructAdmPosition,
    UsersPosition,
)
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select
from sqlalchemy_utils import Ltree

from ..fixtures.factories import make_event
from ..kafka.test_kafka_events import create_company, create_user


async def create_root_structure(session, company_id: uuid.UUID) -> StructAdm:
    root = StructAdm(id=uuid.uuid4(), company_id=company_id, name="Root", path=Ltree(f"c{company_id.hex}"))
    session.add(root)
    await session.commit()

    return root


@pytest.mark.asyncio
async def test_create_user_position(session):
    company_id = uuid.uuid4()
    user_id = uuid.uuid4()
    position_id = uuid.uuid4()
    correlation_id = uuid.uuid4()
    saga_id = uuid.uuid4()
    invite_id = uuid.uuid4()

    await create_company(session, company_id=company_id)
    await create_user(session, user_id=user_id, company_id=company_id)

    root = await create_root_structure(session=session, company_id=company_id)
    assert root is not None

    position = Position(id=position_id, company_id=company_id, name="Backend Developer")
    session.add(position)
    await session.commit()

    struct_adm_position = StructAdmPosition(struct_adm_id=root.id, position_id=position.id)
    session.add(struct_adm_position)
    await session.commit()

    event = make_event(
        event_type="registration.org.provision",
        aggregate_id=user_id,
        correlation_id=correlation_id,
        payload={
            "saga_id": str(saga_id),
            "user_id": str(user_id),
            "company_id": str(company_id),
            "struct_adm_id": str(root.id),
            "position_id": str(position.id),
            "invite_id": str(invite_id),
            "first_name": "Ivan",
            "last_name": "Ivanov",
        },
    )

    uow = PostgreSQLOrgUnitOfWork(session)

    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    users_position = await session.scalar(
        select(UsersPosition).where(UsersPosition.user_id == user_id, UsersPosition.position_id == position_id)
    )

    assert users_position is not None

    completed_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "registration.org.completed", OutboxEvent.correlation_id == correlation_id
        )
    )

    assert completed_event is not None
    assert completed_event.aggregate_id == saga_id
