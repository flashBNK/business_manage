from uuid import UUID

import pytest
from infrastructure.databases.postgresql.models import UsersPosition
from sqlalchemy import select

from ..fixtures.db import (
    create_company,
    create_position,
    create_root_structure,
    create_struct_adm_position,
    create_user,
)


@pytest.mark.asyncio
async def test_manager_lifecycle_and_authorization(client, session, set_auth_token):
    company = await create_company(session)
    root = await create_root_structure(session, company.id)
    user = await create_user(session, company_id=company.id, username="Ivan Ivanov")
    position = await create_position(session, company.id, name="Backend Developer")

    await create_struct_adm_position(session, struct_adm_id=root.id, position_id=position.id)
    set_auth_token(company.id)

    users_position = await client.post(
        f"/api/v1/companies/{company.id}/structure/{root.id}/employees",
        json={"user_id": str(user.id), "position_id": str(position.id)},
    )
    assert users_position.status_code == 201

    set_auth_token(company.id)

    response = await client.put(
        f"/api/v1/companies/{company.id}/structure/{root.id}/manager",
        json={"user_id": str(user.id), "position_id": str(position.id)},
    )
    assert response.status_code == 200

    manager = response.json()
    assert UUID(manager["user_id"]) == user.id
    assert UUID(manager["struct_adm_id"]) == root.id
    assert UUID(manager["position_id"]) == position.id
    assert manager["role"] == "manager"

    set_auth_token(company.id)

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/manager")
    assert response.status_code == 200

    manager = response.json()
    assert UUID(manager["user_id"]) == user.id
    assert manager["role"] == "manager"

    response = await client.put(
        f"/api/v1/companies/{company.id}/structure/{root.id}/manager",
        json={"user_id": str(user.id), "position_id": str(position.id)},
    )
    assert response.status_code == 200

    other_company_id = (await create_company(session, name="Another Company")).id

    set_auth_token(other_company_id)

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/manager")
    assert response.status_code == 403

    set_auth_token(company.id)

    response = await client.request(
        "DELETE",
        f"/api/v1/companies/{company.id}/structure/{root.id}/manager",
        json={"user_id": str(user.id), "position_id": str(position.id)},
    )
    assert response.status_code == 200

    deleted_manager = response.json()
    assert UUID(deleted_manager["user_id"]) == user.id
    assert deleted_manager["role"] == "member"

    users_position = await session.scalar(
        select(UsersPosition).where(
            UsersPosition.user_id == user.id,
            UsersPosition.position_id == position.id,
            UsersPosition.struct_adm_id == root.id,
        )
    )

    assert users_position is not None
    assert users_position.role.value == "member"

    set_auth_token(company.id)

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/manager")
    assert response.status_code == 404
