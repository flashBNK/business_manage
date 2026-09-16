from uuid import UUID

import pytest
from infrastructure.databases.postgresql.models import UsersPosition
from sqlalchemy import select

from ..fixtures.db import create_company, create_root_structure, create_user


@pytest.mark.asyncio
async def test_users_position_full_lifecycle(client, session, set_auth_token):
    company = await create_company(session)
    root = await create_root_structure(session, company.id, name="Root")
    user = await create_user(session, company_id=company.id, username="Ivan Ivanov")

    set_auth_token(company.id)

    response = await client.post(f"/api/v1/companies/{company.id}/structure/{root.id}/children", json={"name": "IT"})
    assert response.status_code == 201

    child_id = UUID(response.json()["id"])

    response = await client.post(f"/api/v1/companies/{company.id}/positions", json={"name": "Backend Developer"})
    assert response.status_code == 201

    child_position_id = UUID(response.json()["id"])

    response = await client.post(f"/api/v1/companies/{company.id}/positions", json={"name": "Team Lead"})
    assert response.status_code == 201

    root_position_id = UUID(response.json()["id"])

    response = await client.post(f"/api/v1/companies/{company.id}/structure/{child_id}/positions/{child_position_id}")
    assert response.status_code == 201

    response = await client.post(f"/api/v1/companies/{company.id}/structure/{root.id}/positions/{root_position_id}")
    assert response.status_code == 201

    response = await client.post(
        f"/api/v1/companies/{company.id}/structure/{child_id}/employees",
        json={"user_id": str(user.id), "position_id": str(child_position_id)},
    )
    assert response.status_code == 201

    created = response.json()

    assert UUID(created["user_id"]) == user.id
    assert UUID(created["position_id"]) == child_position_id
    assert UUID(created["struct_adm_id"]) == child_id
    assert created["role"] == "member"

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/employees")
    assert response.status_code == 200

    result = response.json()
    assert result["total"] == 0
    assert result["employees"] == []

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/employees?include_children=true")
    assert response.status_code == 200

    result = response.json()
    assert result["total"] == 1

    employee = result["employees"][0]

    assert UUID(employee["user_id"]) == user.id
    assert employee["username"] == "Ivan Ivanov"
    assert UUID(employee["position_id"]) == child_position_id
    assert employee["position_name"] == "Backend Developer"
    assert employee["role"] == "member"

    response = await client.patch(
        f"/api/v1/companies/{company.id}/structure/{child_id}/positions/{child_position_id}/employees/{user.id}",
        json={"struct_adm_id": str(root.id), "position_id": str(root_position_id)},
    )
    assert response.status_code == 200

    updated = response.json()

    assert UUID(updated["user_id"]) == user.id
    assert UUID(updated["struct_adm_id"]) == root.id
    assert UUID(updated["position_id"]) == root_position_id
    assert updated["role"] == "member"

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{child_id}/employees")
    assert response.status_code == 200
    assert response.json()["total"] == 0

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/employees")
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = await client.delete(
        f"/api/v1/companies/{company.id}/structure/{root.id}/positions/{root_position_id}/employees/{user.id}"
    )
    assert response.status_code == 204

    db_users_position = await session.scalar(
        select(UsersPosition).where(
            UsersPosition.user_id == user.id,
            UsersPosition.position_id == root_position_id,
            UsersPosition.struct_adm_id == root.id,
        )
    )
    assert db_users_position is None
