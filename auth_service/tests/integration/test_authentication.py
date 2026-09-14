from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from infrastructure.databases.postgresql.models.refresh_token import RefreshToken
from infrastructure.security.hash_token import hash_token

from .test_registration import register_user


@pytest.mark.asyncio
async def test_login_refresh_logout_flow(client, session):
    email = "authentication@example.com"
    password = "StrongPassword123!"
    company_name = "Authentication Company"

    registered = await register_user(client, session, email=email, password=password, company_name=company_name)
    login_response = await client.post("/api/v1/login", json={"email": email, "password": password})

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert login_data["access_token"]
    assert login_data["refresh_token"]

    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    wrong_password_response = await client.post("/api/v1/login", json={"email": email, "password": "WrongPassword321!"})

    assert wrong_password_response.status_code == 401
    assert wrong_password_response.json()["detail"] == "Invalid email or password"

    me_response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {access_token}"})

    assert me_response.status_code == 200

    me_data = me_response.json()

    assert me_data["User"] == str(registered["user_id"])
    assert len(me_data["memberships"]) == 1
    assert me_data["memberships"][0]["company_id"] == str(registered["company_id"])
    assert me_data["memberships"][0]["role"] == "owner"

    refresh_response = await client.post("/api/v1/refresh", json={"refresh_token": refresh_token})

    assert refresh_response.status_code == 200

    refresh_data = refresh_response.json()

    assert refresh_data["access_token"]
    assert refresh_data["refresh_token"]

    new_access_token = refresh_data["access_token"]
    new_refresh_token = refresh_data["refresh_token"]

    assert new_refresh_token != refresh_token

    old_refresh_row = (
        await session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == hash_token(refresh_token)))
    ).scalar_one()

    assert old_refresh_row.revoked_at is not None

    new_refresh_row = (
        await session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == hash_token(new_refresh_token)))
    ).scalar_one()

    assert new_refresh_row.user_id == registered["user_id"]
    assert new_refresh_row.revoked_at is None
    assert new_refresh_row.expires_at > datetime.now(UTC)

    new_me_response = await client.get("/api/v1/me", headers={"Authorization": f"Bearer {new_access_token}"})

    assert new_me_response.status_code == 200

    new_me_data = new_me_response.json()

    assert new_me_data["User"] == str(registered["user_id"])

    old_refresh_response = await client.post("/api/v1/refresh", json={"refresh_token": refresh_token})

    assert old_refresh_response.status_code == 401
    assert old_refresh_response.json()["detail"] == "Invalid refresh token"

    logout_response = await client.post("/api/v1/logout", json={"refresh_token": new_refresh_token})

    assert logout_response.status_code == 204

    after_logout_response = await client.post("/api/v1/refresh", json={"refresh_token": new_refresh_token})

    assert after_logout_response.status_code == 401
    assert after_logout_response.json()["detail"] == "Invalid refresh token"

    final_token_row = (
        await session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == hash_token(new_refresh_token)))
    ).scalar_one()

    assert final_token_row.revoked_at is not None