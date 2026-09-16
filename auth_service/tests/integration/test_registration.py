import pytest
from infrastructure.databases.postgresql.models.invite import Invite, InviteStatus
from infrastructure.databases.postgresql.models.members import MemberRoles
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.refresh_token import RefreshToken
from infrastructure.databases.postgresql.models.user import UserStatus
from sqlalchemy import select

from .register_user import register_user


@pytest.mark.asyncio
async def test_full_user_registration_flow(client, session):
    email = "registration@example.com"
    password = "StrongPassword123!"
    company_name = "Registration Company"

    result = await register_user(
        client,
        session,
        email=email,
        password=password,
        first_name="John",
        last_name="Smith",
        company_name=company_name,
    )

    user = result["user"]
    company = result["company"]
    member = result["member"]
    account = result["account"]

    assert account.email == email
    assert account.is_verified is True
    assert account.verified_at is not None

    assert user.first_name == "John"
    assert user.last_name == "Smith"
    assert user.status == UserStatus.ACTIVE

    assert company.name == company_name
    assert company.is_active is True

    assert member.user_id == user.id
    assert member.company_id == company.id
    assert member.role == MemberRoles.OWNER
    assert member.is_active is True

    invite = (await session.execute(select(Invite).where(Invite.email == email))).scalar_one()

    assert invite.status == InviteStatus.ACCEPTED
    assert invite.accepted_at is not None

    refresh_tokens = (
        (await session.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars().all()
    )

    assert len(refresh_tokens) == 1
    assert refresh_tokens[0].revoked_at is None
    assert refresh_tokens[0].expires_at > invite.accepted_at

    outbox_events = (
        (
            await session.execute(
                select(OutboxEvent)
                .where(OutboxEvent.aggregate_id.in_([user.id, company.id]))
                .order_by(OutboxEvent.occurred_at)
            )
        )
        .scalars()
        .all()
    )

    event_types = {event.event_type for event in outbox_events}

    assert "company.created" in event_types
    assert "employee.created" in event_types

    employee_created = next(event for event in outbox_events if event.event_type == "employee.created")

    assert employee_created.producer == "auth_service"
    assert employee_created.payload["user_id"] == str(user.id)
    assert employee_created.payload["company_id"] == str(company.id)
    assert employee_created.payload["email"] == email
    assert employee_created.payload["first_name"] == "John"
    assert employee_created.payload["last_name"] == "Smith"
    assert employee_created.payload["role"] == MemberRoles.OWNER.value
    assert employee_created.payload["is_active"] is True

    response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {result['access_token']}"})

    assert response.status_code == 200

    me = response.json()

    assert me["User"] == str(user.id)
    assert len(me["memberships"]) == 1
    assert me["memberships"][0]["company_id"] == str(company.id)
    assert me["memberships"][0]["role"] == MemberRoles.OWNER.value
