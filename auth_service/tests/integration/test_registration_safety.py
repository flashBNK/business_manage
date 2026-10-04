import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from app import app
from httpx import ASGITransport, AsyncClient
from infrastructure.databases.postgresql.models.account import Account
from infrastructure.databases.postgresql.models.invite import Invite
from infrastructure.databases.postgresql.models.secret import Secret
from infrastructure.databases.postgresql.models.ticket import Ticket
from infrastructure.databases.postgresql.session import get_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def complete_payload(email: str, code: str) -> dict:
    return {
        "email": email,
        "code": code,
        "password": "StrongPassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": None,
    }


async def confirm_email(client, session, email: str) -> str:
    response = await client.post("/api/v1/check_account", json={"email": email})
    assert response.status_code == 201

    invite = await session.scalar(select(Invite).where(Invite.email == email))
    response = await client.post("/api/v1/sign-up", json={"email": email, "code": invite.code})
    assert response.status_code == 201
    return response.json()["ticket"]


@pytest.mark.asyncio
async def test_cannot_complete_registration_before_email_confirmation(client, session):
    email = "unconfirmed@example.com"
    response = await client.post("/api/v1/check_account", json={"email": email})
    assert response.status_code == 201

    response = await client.post("/api/v1/sign-up-complete", json=complete_payload(email, "wrong-ticket"))
    assert response.status_code == 409
    assert await session.scalar(select(Account).where(Account.email == email)) is None


@pytest.mark.asyncio
async def test_registration_ticket_is_bound_to_email(client, session):
    first_ticket = await confirm_email(client, session, "first@example.com")
    await confirm_email(client, session, "second@example.com")

    response = await client.post(
        "/api/v1/sign-up-complete",
        json=complete_payload("second@example.com", first_ticket),
    )
    assert response.status_code == 409

    account = await session.scalar(select(Account).where(Account.email == "second@example.com"))
    assert await session.scalar(select(Secret).where(Secret.account_id == account.id)) is None


@pytest.mark.asyncio
async def test_expired_registration_ticket_is_rejected(client, session):
    email = "expired-ticket@example.com"
    code = await confirm_email(client, session, email)
    ticket = await session.scalar(select(Ticket).where(Ticket.code == code))
    ticket.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    await session.commit()

    response = await client.post("/api/v1/sign-up-complete", json=complete_payload(email, code))
    assert response.status_code == 409

    account = await session.scalar(select(Account).where(Account.email == email))
    assert await session.scalar(select(Secret).where(Secret.account_id == account.id)) is None


@pytest.mark.asyncio
async def test_registration_ticket_cannot_be_used_twice(client, session):
    email = "used-ticket@example.com"
    code = await confirm_email(client, session, email)

    response = await client.post("/api/v1/sign-up-complete", json=complete_payload(email, code))
    assert response.status_code == 201

    response = await client.post("/api/v1/sign-up-complete", json=complete_payload(email, code))
    assert response.status_code == 409

    ticket = await session.scalar(select(Ticket).where(Ticket.code == code))
    assert (
        ticket is None
        or getattr(ticket, "used_at", None) is not None
        or getattr(ticket, "consumed_at", None) is not None
    )


@pytest.mark.asyncio
async def test_wrong_email_codes_count_towards_limit(client, session, engine):
    email = "wrong-codes@example.com"
    response = await client.post("/api/v1/check_account", json={"email": email})
    assert response.status_code == 201

    for _ in range(5):
        response = await client.post("/api/v1/sign-up", json={"email": email, "code": "wrong"})
        assert response.status_code in (400, 429)

    async with engine.connect() as connection:
        attempts = await connection.scalar(select(Invite.attempts).where(Invite.email == email))
    assert attempts == 5

    response = await client.post("/api/v1/sign-up", json={"email": email, "code": "wrong"})
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_parallel_wrong_email_codes_are_counted(client, engine):
    email = "parallel-codes@example.com"
    response = await client.post("/api/v1/check_account", json={"email": email})
    assert response.status_code == 201

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def get_request_session():
        async with session_factory() as request_session:
            yield request_session

    original_override = app.dependency_overrides[get_async_session]
    app.dependency_overrides[get_async_session] = get_request_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as concurrent_client:
            responses = await asyncio.gather(
                concurrent_client.post("/api/v1/sign-up", json={"email": email, "code": "wrong"}),
                concurrent_client.post("/api/v1/sign-up", json={"email": email, "code": "wrong"}),
            )
    finally:
        app.dependency_overrides[get_async_session] = original_override

    assert [response.status_code for response in responses] == [400, 400]
    async with engine.connect() as connection:
        attempts = await connection.scalar(select(Invite.attempts).where(Invite.email == email))
    assert attempts == 2
