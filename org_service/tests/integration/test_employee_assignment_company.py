from uuid import uuid4

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import OutboxEvent, UsersPosition
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy import select

from ..fixtures.db import (
    create_company,
    create_position,
    create_root_structure,
    create_struct_adm_position,
    create_user,
)
from ..fixtures.factories import make_event


async def create_assignment_data(session):
    company = await create_company(session, name="Company A")
    other_company = await create_company(session, name="Company B")
    structure = await create_root_structure(session, company.id)
    other_structure = await create_root_structure(session, other_company.id)
    position = await create_position(session, company.id)
    other_position = await create_position(session, other_company.id)
    user = await create_user(session, company_id=company.id)
    other_user = await create_user(session, company_id=other_company.id)

    await create_struct_adm_position(session, structure.id, position.id)
    await create_struct_adm_position(session, structure.id, other_position.id)
    await create_struct_adm_position(session, other_structure.id, position.id)

    return company, structure, position, user, other_structure, other_position, other_user


@pytest.mark.parametrize("foreign_part", ["user", "structure", "position"])
@pytest.mark.asyncio
async def test_http_rejects_assignment_from_another_company(client, session, set_auth_token, foreign_part):
    company, structure, position, user, other_structure, other_position, other_user = await create_assignment_data(
        session
    )
    set_auth_token(company.id)

    user_id = other_user.id if foreign_part == "user" else user.id
    structure_id = other_structure.id if foreign_part == "structure" else structure.id
    position_id = other_position.id if foreign_part == "position" else position.id

    response = await client.post(
        f"/api/v1/companies/{company.id}/structure/{structure_id}/employees",
        json={"user_id": str(user_id), "position_id": str(position_id)},
    )
    assert response.status_code == 404

    assignment = await session.scalar(
        select(UsersPosition).where(
            UsersPosition.user_id == user_id,
            UsersPosition.struct_adm_id == structure_id,
            UsersPosition.position_id == position_id,
        )
    )
    assert assignment is None


@pytest.mark.parametrize("foreign_part", ["user", "structure", "position"])
@pytest.mark.asyncio
async def test_saga_rejects_assignment_from_another_company(session, foreign_part):
    company, structure, position, user, other_structure, other_position, other_user = await create_assignment_data(
        session
    )

    user_id = other_user.id if foreign_part == "user" else user.id
    structure_id = other_structure.id if foreign_part == "structure" else structure.id
    position_id = other_position.id if foreign_part == "position" else position.id
    saga_id = uuid4()

    event = make_event(
        event_type="registration.org.provision",
        aggregate_id=user_id,
        payload={
            "saga_id": str(saga_id),
            "user_id": str(user_id),
            "company_id": str(company.id),
            "struct_adm_id": str(structure_id),
            "position_id": str(position_id),
            "invite_id": str(uuid4()),
        },
    )

    uow = PostgreSQLOrgUnitOfWork(session)
    async with uow:
        await EVENT_HANDLERS[event["event_type"]](EventEnvelopeDTO.from_dict(event), uow)

    assignment = await session.scalar(
        select(UsersPosition).where(
            UsersPosition.user_id == user_id,
            UsersPosition.struct_adm_id == structure_id,
            UsersPosition.position_id == position_id,
        )
    )
    assert assignment is None

    failed_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "registration.org.failed",
            OutboxEvent.aggregate_id == saga_id,
        )
    )
    assert failed_event is not None

    position_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "employee.position.changed",
            OutboxEvent.aggregate_id == user_id,
        )
    )
    assert position_event is None
