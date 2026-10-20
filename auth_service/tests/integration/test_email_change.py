import pytest
from infrastructure.databases.postgresql.models.account import Account
from infrastructure.databases.postgresql.models.invite import Invite
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.kafka.producer.producer_loop import TOPIC_EVENT_TYPE
from sqlalchemy import select

from .register_user import register_user


@pytest.mark.asyncio
async def test_email_change_creates_event(client, session):
    old_email = "old@example.com"
    new_email = "new@example.com"
    password = "StrongPassword123!"
    user = await register_user(client, session, email=old_email, password=password)
    account_id = user["account"].id
    headers = {"Authorization": f"Bearer {user['access_token']}"}

    response = await client.post(f"/api/v1/account/{account_id}", json={"new_email": new_email}, headers=headers)
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/account/{account_id}/update-complete", json={"invite_code": "wrong-code"}, headers=headers
    )
    assert response.status_code == 409
    assert await session.scalar(select(Account.email).where(Account.id == account_id)) == old_email
    assert await session.scalar(select(OutboxEvent).where(OutboxEvent.event_type == "employee.email.changed")) is None

    code = await session.scalar(select(Invite.code).where(Invite.email == new_email))
    response = await client.post(
        f"/api/v1/account/{account_id}/update-complete", json={"invite_code": code}, headers=headers
    )
    assert response.status_code == 201
    assert response.json()["email"] == new_email
    assert await session.scalar(select(Account.email).where(Account.id == account_id)) == new_email

    response = await client.post(
        f"/api/v1/account/{account_id}/update-complete", json={"invite_code": code}, headers=headers
    )
    assert response.status_code == 409

    event = (
        await session.execute(select(OutboxEvent).where(OutboxEvent.event_type == "employee.email.changed"))
    ).scalar_one()
    assert event.aggregate_id == user["user_id"]
    assert event.payload == {"user_id": str(user["user_id"]), "old_email": old_email, "new_email": new_email}
    assert event.published_at is None
    assert TOPIC_EVENT_TYPE[event.event_type] == "auth.employee.events"

    response = await client.post("/api/v1/login", json={"email": new_email, "password": password})
    assert response.status_code == 200

    response = await client.post("/api/v1/login", json={"email": old_email, "password": password})
    assert response.status_code == 401
