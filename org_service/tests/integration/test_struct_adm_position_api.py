from uuid import UUID

import pytest
from infrastructure.databases.postgresql.models import StructAdmPosition
from sqlalchemy import select

from ..fixtures.db import create_company, create_position, create_root_structure


@pytest.mark.asyncio
async def test_struct_adm_position_lifecycle(client, session, set_auth_token):
    company_a = await create_company(session, name="Company A")
    company_b = await create_company(session, name="Company B")
    root_a = await create_root_structure(session, company_a.id)
    position_a = await create_position(session, company_a.id, name="Backend Developer")
    position_b = await create_position(session, company_b.id, name="Backend Developer")

    set_auth_token(company_a.id)

    response = await client.post(f"/api/v1/companies/{company_a.id}/structure/{root_a.id}/positions/{position_a.id}")
    assert response.status_code == 201

    body = response.json()
    assert UUID(body["struct_adm_id"]) == root_a.id
    assert UUID(body["position_id"]) == position_a.id

    relation = await session.scalar(
        select(StructAdmPosition).where(
            StructAdmPosition.struct_adm_id == root_a.id, StructAdmPosition.position_id == position_a.id
        )
    )
    assert relation is not None

    response = await client.post(f"/api/v1/companies/{company_a.id}/structure/{root_a.id}/positions/{position_b.id}")
    assert response.status_code == 404

    response = await client.delete(f"/api/v1/companies/{company_a.id}/structure/{root_a.id}/positions/{position_a.id}")
    assert response.status_code == 204

    relation = await session.scalar(
        select(StructAdmPosition).where(
            StructAdmPosition.struct_adm_id == root_a.id, StructAdmPosition.position_id == position_a.id
        )
    )
    assert relation is None
