from httpx import AsyncClient
from infrastructure.databases.postgresql.models.account import Account
from infrastructure.databases.postgresql.models.company import Company
from infrastructure.databases.postgresql.models.invite import Invite
from infrastructure.databases.postgresql.models.members import Members
from infrastructure.databases.postgresql.models.secret import Secret
from infrastructure.databases.postgresql.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def register_user(
    client: AsyncClient,
    session: AsyncSession,
    email: str,
    password: str,
    first_name: str = "John",
    last_name: str = "Doe",
    company_name: str | None = None,
) -> dict:
    check_response = await client.post("/api/v1/check_account", json={"email": email})

    assert check_response.status_code == 201

    invite_result = await session.execute(select(Invite).where(Invite.email == email))
    invite = invite_result.scalar_one()

    assert invite.code
    assert len(invite.code) == 6
    assert invite.code.isdigit()

    confirm_response = await client.post("/api/v1/sign-up", json={"email": email, "code": invite.code})

    assert confirm_response.status_code == 201

    account = (await session.execute(select(Account).where(Account.email == email))).scalar_one()

    assert account.is_verified is True
    assert account.verified_at is not None

    complete_response = await client.post(
        "/api/v1/sign-up-complete",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "company_name": company_name,
        },
    )

    assert complete_response.status_code == 201

    token_data = complete_response.json()

    assert token_data["access_token"]
    assert token_data["refresh_token"]

    user = (
        await session.execute(
            select(User).join(Secret, Secret.user_id == User.id).where(Secret.account_id == account.id)
        )
    ).scalar_one()

    company = None
    member = None

    if company_name is not None:
        company = (await session.execute(select(Company).where(Company.name == company_name))).scalar_one()

        member = (
            await session.execute(select(Members).where(Members.user_id == user.id, Members.company_id == company.id))
        ).scalar_one()

    return {
        "account": account,
        "user": user,
        "company": company,
        "member": member,
        "invite": invite,
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "user_id": user.id,
        "company_id": company.id if company else None,
    }
