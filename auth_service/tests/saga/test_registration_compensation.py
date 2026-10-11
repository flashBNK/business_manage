from uuid import uuid4

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.account import Account
from infrastructure.databases.postgresql.models.invite import Invite, InviteStatus
from infrastructure.databases.postgresql.models.members import Members
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.databases.postgresql.models.user import User
from infrastructure.kafka.consumer.handlers import handle_employee_registered, handle_org_failed
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy import select
from usecases.registration.compensate.implementation import PostgreSQLCompensateRegistrationUseCase

from .conftest import create_employee, make_event, outbox_to_event


@pytest.mark.asyncio
async def test_onboarding_failure_preserves_user_and_revokes_invite(client, session, admin):
    employee = await create_employee(client, session, admin, uuid4(), uuid4())
    user_id = employee["user_id"]
    invite_id = employee["invite"].id
    payload = {"invite_token": employee["invite"].code, "password": employee["password"]}

    response = await client.post("/api/v1/employees/invite-complete", json=payload)
    assert response.status_code == 201
    tokens = response.json()

    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert response.status_code == 200
    assert response.json()["memberships"] == []

    member = await session.scalar(select(Members).where(Members.invite_id == invite_id))
    assert member.is_active is False
    invite = await session.get(Invite, invite_id)
    account_id = invite.account_id

    registered = await session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_type == "employee.registered", OutboxEvent.aggregate_id == user_id)
    )
    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_employee_registered(event=EventEnvelopeDTO.from_dict(outbox_to_event(registered)), uow=uow)

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.invite_id == invite_id))
    saga_id = saga.id
    failed = EventEnvelopeDTO.from_dict(
        make_event("registration.org.failed", saga_id, saga.correlation_id, {"reason": "position not found"})
    )

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        saga = await uow.registration_saga.get(saga_id=saga_id)
        await handle_org_failed(event=failed, uow=uow)

    for _ in range(2):
        async with PostgreSQLAuthUnitOfWork(session=session) as uow:
            await PostgreSQLCompensateRegistrationUseCase(uow=uow).execute(
                saga=saga, reason="position not found", causation_id=failed.event_id
            )

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_org_failed(event=failed, uow=uow)

    saga = await session.get(RegistrationSaga, saga_id)
    assert saga.status == RegistrationStatus.FAILED
    assert saga.last_error == "position not found"
    assert await session.get(User, user_id) is not None
    assert await session.get(Account, account_id) is not None

    invite = await session.get(Invite, invite_id)
    assert invite is not None
    assert invite.status == InviteStatus.REVOKED
    member = await session.scalar(select(Members).where(Members.invite_id == invite_id))
    assert member is not None
    assert member.is_active is False

    events = await session.scalars(
        select(OutboxEvent).where(OutboxEvent.event_type == "registration.failed", OutboxEvent.aggregate_id == saga_id)
    )
    assert len(events.all()) == 1

    response = await client.post("/api/v1/employees/invite-complete", json=payload)
    assert response.status_code == 409

    response = await client.post("/api/v1/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["memberships"] == []
