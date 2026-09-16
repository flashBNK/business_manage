from uuid import UUID

import pytest
from api.v1.token_dependencies import get_current_token
from app import app
from domain.token.models import MemberRoles, MembershipAdmission, TokenDTO
from infrastructure.databases.postgresql.models import Position
from sqlalchemy import select

from ..fixtures.db import create_company


@pytest.mark.asyncio
async def test_position_lifecycle(client, session, set_auth_token):
    company_a = await create_company(session, name="Company A")
    company_b = await create_company(session, name="Company B")

    set_auth_token(company_a.id)

    response = await client.post(
        f"/api/v1/companies/{company_a.id}/positions",
        json={"name": "Backend Developer", "description": "Python backend developer"},
    )
    assert response.status_code == 201

    created = response.json()
    position_id = UUID(created["id"])

    assert created["company_id"] == str(company_a.id)
    assert created["name"] == "Backend Developer"
    assert created["description"] == "Python backend developer"

    response = await client.get(f"/api/v1/companies/{company_a.id}/positions/{position_id}")
    assert response.status_code == 200

    fetched = response.json()
    assert UUID(fetched["id"]) == position_id
    assert fetched["name"] == "Backend Developer"

    response = await client.get(f"/api/v1/companies/{company_a.id}/positions")
    assert response.status_code == 200

    position_list = response.json()
    assert position_list["total"] == 1
    assert UUID(position_list["positions"][0]["id"]) == position_id

    response = await client.patch(
        f"/api/v1/companies/{company_a.id}/positions/{position_id}",
        json={
            "name": "Senior Backend Developer",
            "description": "Senior Python backend developer",
        },
    )
    assert response.status_code == 200

    updated = response.json()
    assert updated["name"] == "Senior Backend Developer"
    assert updated["description"] == "Senior Python backend developer"

    set_auth_token(company_a.id)

    def override_token():
        return TokenDTO(
            subject=UUID(created["id"]),
            memberships=[
                MembershipAdmission(company_id=company_a.id, role=MemberRoles.ADMIN),
                MembershipAdmission(company_id=company_b.id, role=MemberRoles.MEMBER),
            ],
        )

    app.dependency_overrides[get_current_token] = override_token

    response = await client.get(f"/api/v1/companies/{company_b.id}/positions/{position_id}")
    assert response.status_code == 404

    set_auth_token(company_a.id)

    response = await client.delete(f"/api/v1/companies/{company_a.id}/positions/{position_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/companies/{company_a.id}/positions/{position_id}")
    assert response.status_code == 404

    position = await session.scalar(select(Position).where(Position.id == position_id))
    assert position is None
