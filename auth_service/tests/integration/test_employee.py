import uuid

import pytest
from sqlalchemy import select

from infrastructure.databases.postgresql.models.account import Account
from infrastructure.databases.postgresql.models.invite import Invite, InviteStatus
from infrastructure.databases.postgresql.models.members import MemberRoles, Members
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.refresh_token import RefreshToken
from infrastructure.databases.postgresql.models.secret import Secret
from infrastructure.databases.postgresql.models.user import User

from .test_registration import register_user


@pytest.mark.asyncio
async def test_employee_invitation_and_registration_flow(client, session):
    admin_email = "admin@example.com"
    admin_password = "AdminPassword123!"
    employee_email = "employee@example.com"
    employee_password = "EmployeePassword123!"
    struct_adm_id = uuid.uuid4()
    position_id = uuid.uuid4()

    admin = await register_user(
        client,
        session,
        email=admin_email,
        password=admin_password,
        first_name="Admin",
        last_name="User",
        company_name="Employee Test Company",
    )

    company_id = admin["company_id"]

    assert company_id is not None

    create_employee_response = await client.post(
        f"/api/v1/companies/{company_id}/employees",
        json={
            "email": employee_email,
            "first_name": "Employee",
            "last_name": "User",
            "role": MemberRoles.MEMBER.value,
            "struct_adm_id": str(struct_adm_id),
            "position_id": str(position_id)
        },
        headers={"Authorization": f"Bearer {admin['access_token']}"})

    assert create_employee_response.status_code == 201

    employee_result = create_employee_response.json()

    employee_user_id = uuid.UUID(employee_result["user_id"])
    employee_member_id = uuid.UUID(employee_result["member_id"])
    employee_user = (await session.execute(select(User).where(User.id == employee_user_id))).scalar_one()

    assert employee_user.first_name == "Employee"
    assert employee_user.last_name == "User"

    invite = (await session.execute(select(Invite).where(Invite.user_id == employee_user_id))).scalar_one()

    assert invite.email == employee_email
    assert invite.status == InviteStatus.PENDING
    assert invite.user_id == employee_user_id
    assert invite.struct_adm_id == struct_adm_id
    assert invite.position_id == position_id
    assert invite.code

    employee_invite_code = invite.code

    member = (await session.execute(select(Members).where(Members.id == employee_member_id))).scalar_one()

    assert member.user_id == employee_user_id
    assert member.company_id == company_id
    assert member.role == MemberRoles.MEMBER
    assert member.is_active is False
    assert member.invite_id == invite.id

    employee_created_event = (
        await session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.event_type == "employee.created", OutboxEvent.aggregate_id == employee_user_id))
    ).scalar_one()

    assert employee_created_event.producer == "auth_service"
    assert employee_created_event.payload["user_id"] == str(employee_user_id)
    assert employee_created_event.payload["company_id"] == str(company_id)
    assert employee_created_event.payload["email"] == employee_email
    assert employee_created_event.payload["first_name"] == "Employee"
    assert employee_created_event.payload["last_name"] == "User"
    assert employee_created_event.payload["role"] == MemberRoles.MEMBER.value
    assert employee_created_event.payload["is_active"] is False

    complete_response = await client.post(
        "/api/v1/employees/invite-complete",
        json={"invite_token": employee_invite_code, "password": employee_password}
    )

    assert complete_response.status_code == 201

    complete_data = complete_response.json()

    assert complete_data["access_token"]
    assert complete_data["refresh_token"]

    employee_access_token = complete_data["access_token"]
    employee_refresh_token = complete_data["refresh_token"]

    invite = (await session.execute(select(Invite).where(Invite.id == invite.id))).scalar_one()

    assert invite.status == InviteStatus.ACCEPTED
    assert invite.accepted_at is not None
    assert invite.account_id is not None

    member = (await session.execute(select(Members).where(Members.id == employee_member_id))).scalar_one()

    assert member.is_active is True

    account = (await session.execute(select(Account).where(Account.id == invite.account_id))).scalar_one()

    assert account.email == employee_email
    assert account.is_verified is True

    secret = (await session.execute(select(Secret).where(Secret.user_id == employee_user_id))).scalar_one()

    assert secret.account_id == account.id
    assert secret.password_hash != employee_password
    assert secret.password_hash

    refresh_token_count = (
        await session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == employee_user_id))
    ).scalars().all()

    assert len(refresh_token_count) == 1
    assert refresh_token_count[0].revoked_at is None

    employee_registered_event = (
        await session.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.event_type == "employee.registered",
                OutboxEvent.aggregate_id == employee_user_id
            )
        )
    ).scalar_one()

    assert employee_registered_event.producer == "auth_service"
    assert employee_registered_event.payload["user_id"] == str(employee_user_id)
    assert employee_registered_event.payload["company_id"] == str(company_id)
    assert employee_registered_event.payload["email"] == employee_email
    assert employee_registered_event.payload["first_name"] == "Employee"
    assert employee_registered_event.payload["last_name"] == "User"
    assert employee_registered_event.payload["role"] == MemberRoles.MEMBER.value
    assert employee_registered_event.payload["is_active"] is True
    assert employee_registered_event.payload["invite_id"] == str(invite.id)
    assert employee_registered_event.payload["struct_adm_id"] == str(struct_adm_id)
    assert employee_registered_event.payload["position_id"] == str(position_id)

    me_response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {employee_access_token}"})

    assert me_response.status_code == 200

    me_data = me_response.json()

    assert me_data["User"] == str(employee_user_id)
    assert len(me_data["memberships"]) == 1
    assert me_data["memberships"][0]["company_id"] == str(company_id)
    assert me_data["memberships"][0]["role"] == MemberRoles.MEMBER.value

    reuse_response = await client.post(
        "/api/v1/employees/invite-complete",
        json={"invite_token": employee_invite_code, "password": employee_password})

    assert reuse_response.status_code == 409

    refresh_response = await client.post( "/api/v1/refresh", json={"refresh_token": employee_refresh_token})

    assert refresh_response.status_code == 200

    refresh_data = refresh_response.json()

    assert refresh_data["access_token"]
    assert refresh_data["refresh_token"]