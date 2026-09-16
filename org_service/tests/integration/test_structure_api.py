from uuid import UUID

import pytest
from infrastructure.databases.postgresql.models import OutboxEvent
from sqlalchemy import select

from ..fixtures.db import create_company, create_root_structure


def find_node(node: dict, node_id: UUID) -> dict | None:
    if UUID(node["id"]) == node_id:
        return node

    for child in node.get("children", []):
        result = find_node(child, node_id)
        if result is not None:
            return result

    return None


@pytest.mark.asyncio
async def test_structure_tree_lifecycle(client, session, set_auth_token):
    company = await create_company(session)
    root = await create_root_structure(session, company.id)

    set_auth_token(company.id)

    response = await client.post(f"/api/v1/companies/{company.id}/structure/{root.id}/children", json={"name": "IT"})
    assert response.status_code == 201

    it = response.json()
    it_id = UUID(it["id"])

    assert it["company_id"] == str(company.id)
    assert it["name"] == "IT"
    assert it["path"] == f"{root.path}.n{it_id.hex}"

    response = await client.post(f"/api/v1/companies/{company.id}/structure/{root.id}/children", json={"name": "HR"})
    assert response.status_code == 201

    hr = response.json()
    hr_id = UUID(hr["id"])

    assert hr["path"] == f"{root.path}.n{hr_id.hex}"

    response = await client.post(
        f"/api/v1/companies/{company.id}/structure/{it_id}/children", json={"name": "Backend"}
    )
    assert response.status_code == 201

    backend = response.json()
    backend_id = UUID(backend["id"])

    assert backend["path"] == f"{it['path']}.n{backend_id.hex}"

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{root.id}/children")
    assert response.status_code == 200

    children = response.json()
    assert {UUID(item["id"]) for item in children} == {it_id, hr_id}

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{it_id}/descendants")
    assert response.status_code == 200

    descendants = response.json()
    assert {UUID(item["id"]) for item in descendants} == {it_id, backend_id}

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{backend_id}/ancestors")
    assert response.status_code == 200

    ancestors = response.json()
    assert {UUID(item["id"]) for item in ancestors} == {root.id, it_id, backend_id}

    response = await client.patch(f"/api/v1/companies/{company.id}/structure/{it_id}", json={"name": "Engineering"})
    assert response.status_code == 200

    renamed = response.json()
    assert renamed["name"] == "Engineering"
    assert renamed["path"] == it["path"]

    response = await client.patch(
        f"/api/v1/companies/{company.id}/structure/{it_id}/move", json={"new_parent_id": str(backend_id)}
    )
    assert response.status_code == 400

    response = await client.patch(
        f"/api/v1/companies/{company.id}/structure/{backend_id}/move", json={"new_parent_id": str(hr_id)}
    )
    assert response.status_code == 200

    moved = response.json()
    expected_path = f"{hr['path']}.n{backend_id.hex}"

    assert moved["path"] == expected_path
    assert moved["name"] == "Backend"

    response = await client.get(f"/api/v1/companies/{company.id}/structure/{it_id}")

    assert response.status_code == 200
    assert response.json()["path"] == it["path"]

    response = await client.get(f"/api/v1/companies/{company.id}/structure")
    assert response.status_code == 200

    tree = response.json()
    assert UUID(tree["id"]) == company.id
    assert tree["name"] == company.name

    root_node = find_node(tree, root.id)
    assert root_node is not None

    root_children = {UUID(child["id"]): child for child in root_node["children"]}
    assert set(root_children) == {it_id, hr_id}

    engineering_node = root_children[it_id]
    hr_node = root_children[hr_id]

    assert engineering_node["name"] == "Engineering"
    assert engineering_node["children"] == []

    backend_node = find_node(hr_node, backend_id)

    assert backend_node is not None
    assert backend_node["name"] == "Backend"

    events = (
        await session.scalars(select(OutboxEvent).where(OutboxEvent.aggregate_id.in_([it_id, hr_id, backend_id])))
    ).all()

    event_types = {event.event_type for event in events}

    assert "struct_adm.created" in event_types
    assert "struct_adm.updated" in event_types
