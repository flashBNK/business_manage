import uuid

import pytest
from domain.kafka.models import EventEnvelopeDTO
from domain.outbox_event.models import OutboxEventType
from infrastructure.databases.postgresql.models import OutboxEvent, Position, StructAdmPosition, UsersPosition
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select

from ..fixtures.factories import make_event
from ..kafka.test_kafka_events import create_company, create_user
from .test_create_user_position import create_root_structure


@pytest.mark.asyncio
async def test_org_compensate_users_position(session):
    company_id = uuid.uuid4()
    user_id = uuid.uuid4()
    position_id = uuid.uuid4()
    correlation_id = uuid.uuid4()
    saga_id = uuid.uuid4()

    await create_company(session, company_id=company_id)
    await create_user(session, user_id=user_id, company_id=company_id)

    position = Position(id=position_id, company_id=company_id, name="Backend Developer")
    session.add(position)
    await session.commit()

    root = await create_root_structure(session=session, company_id=company_id)

    struct_adm_position = StructAdmPosition(struct_adm_id=root.id, position_id=position.id)
    session.add(struct_adm_position)
    await session.commit()

    users_position = UsersPosition(user_id=user_id, position_id=position_id, struct_adm_id=root.id, role="member")
    session.add(users_position)
    await session.commit()

    assert users_position is not None

    event = make_event(
        event_type="registration.org.compensate",
        aggregate_id=saga_id,
        correlation_id=correlation_id,
        payload={
            "user_id": str(user_id),
            "company_id": str(company_id),
            "saga_id": str(saga_id),
            "struct_adm_id": str(root.id),
            "position_id": str(position_id),
        },
    )

    uow = PostgreSQLOrgUnitOfWork(session)

    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    user_position = await session.scalar(
        select(UsersPosition).where(UsersPosition.user_id == user_id, UsersPosition.position_id == position_id)
    )

    assert user_position is None

    compensated_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "registration.org.compensated", OutboxEvent.correlation_id == correlation_id
        )
    )

    assert compensated_event is not None
    assert compensated_event.aggregate_id == saga_id

    employee_position_deleted = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == OutboxEventType.EMPLOYEE_POSITION_DELETED,
            OutboxEvent.correlation_id == correlation_id,
        )
    )

    assert employee_position_deleted is not None
    assert employee_position_deleted.aggregate_id == user_id
    assert employee_position_deleted.payload["user_id"] == str(user_id)
