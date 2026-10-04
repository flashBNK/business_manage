from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from domain.token.models import MemberRoles
from infrastructure.databases.postgresql.models import OutboxEvent
from sqlalchemy import select

from ..fixtures.factories import create_user


@pytest.mark.asyncio
async def test_update_task_and_replace_participants(client, session, set_auth_token):
    company_id = uuid4()

    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")
    old_watcher = await create_user(session, company_id, "Old Watcher")
    new_watcher = await create_user(session, company_id, "New Watcher")
    old_assignee = await create_user(session, company_id, "Old Assignee")
    new_assignee = await create_user(session, company_id, "New Assignee")

    set_auth_token(company_id, role=MemberRoles.ADMIN, user_id=author.id)

    create_response = await client.post(
        f"/api/v1/companies/{company_id}/tasks",
        json={
            "title": "Initial task",
            "description": "Initial description",
            "responsible_id": str(responsible.id),
            "deadline": (datetime.now(UTC) + timedelta(days=5)).isoformat(),
            "estimated_minutes": 60,
            "watcher_ids": [str(old_watcher.id)],
            "assignee_ids": [str(old_assignee.id)],
        },
    )
    assert create_response.status_code == 201

    task_id = UUID(create_response.json()["id"])
    response = await client.patch(
        f"/api/v1/companies/{company_id}/tasks/{task_id}",
        json={
            "title": "Updated task",
            "description": "Updated description",
            "estimated_minutes": 180,
            "watcher_ids": [str(new_watcher.id)],
            "assignee_ids": [str(new_assignee.id)],
        },
    )
    assert response.status_code == 200

    task = response.json()
    assert task["title"] == "Updated task"
    assert task["description"] == "Updated description"
    assert task["estimated_minutes"] == 180
    assert task["watcher_ids"] == [str(new_watcher.id)]
    assert task["assignee_ids"] == [str(new_assignee.id)]

    response = await client.get(f"/api/v1/companies/{company_id}/tasks/{task_id}")
    assert response.status_code == 200

    task = response.json()
    assert task["watcher_ids"] == [str(new_watcher.id)]
    assert task["assignee_ids"] == [str(new_assignee.id)]

    outbox_events = (
        await session.scalars(
            select(OutboxEvent).where(
                OutboxEvent.aggregate_id == task_id,
                OutboxEvent.event_type == "task.updated",
            )
        )
    ).all()
    assert len(outbox_events) == 1
    assert outbox_events[0].payload["title"] == "Updated task"
    assert outbox_events[0].payload["watcher_ids"] == [str(new_watcher.id)]
    assert outbox_events[0].payload["assignee_ids"] == [str(new_assignee.id)]


@pytest.mark.asyncio
async def test_update_task_keeps_other_task_participants(client, session, set_auth_token):
    company_id = uuid4()

    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")
    watcher = await create_user(session, company_id, "Watcher")
    assignee = await create_user(session, company_id, "Assignee")

    set_auth_token(company_id, role=MemberRoles.ADMIN, user_id=author.id)

    task_ids = []
    for title in ("Task A", "Task B"):
        response = await client.post(
            f"/api/v1/companies/{company_id}/tasks",
            json={
                "title": title,
                "description": "Description",
                "responsible_id": str(responsible.id),
                "deadline": (datetime.now(UTC) + timedelta(days=5)).isoformat(),
                "estimated_minutes": 60,
                "watcher_ids": [str(watcher.id)],
                "assignee_ids": [str(assignee.id)],
            },
        )
        assert response.status_code == 201
        task_ids.append(UUID(response.json()["id"]))

    response = await client.patch(
        f"/api/v1/companies/{company_id}/tasks/{task_ids[0]}",
        json={"watcher_ids": [], "assignee_ids": []},
    )
    assert response.status_code == 200
    assert response.json()["watcher_ids"] == []
    assert response.json()["assignee_ids"] == []

    response = await client.get(f"/api/v1/companies/{company_id}/tasks/{task_ids[1]}")
    assert response.status_code == 200
    assert response.json()["watcher_ids"] == [str(watcher.id)]
    assert response.json()["assignee_ids"] == [str(assignee.id)]
