from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from domain.token.models import MemberRoles
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from sqlalchemy import select

from ..fixtures.factories import create_user


@pytest.mark.asyncio
async def test_create_task(client, session, set_auth_token):
    company_id = uuid4()
    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")
    watcher = await create_user(session, company_id, "Watcher")
    assignee = await create_user(session, company_id, "Assignee")

    payload = {
        "title": "Implement authentication",
        "description": "Create JWT authentication",
        "responsible_id": str(responsible.id),
        "deadline": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "estimated_minutes": 120,
        "watcher_ids": [str(watcher.id)],
        "assignee_ids": [str(assignee.id)],
    }

    set_auth_token(company_id, role=MemberRoles.ADMIN, user_id=author.id)

    response = await client.post(f"/api/v1/companies/{company_id}/tasks", json=payload)
    assert response.status_code == 201

    task = response.json()
    task_id = UUID(task["id"])

    assert task["title"] == payload["title"]
    assert task["description"] == payload["description"]
    assert task["author_id"] == str(author.id)
    assert task["responsible_id"] == str(responsible.id)
    assert task["company_id"] == str(company_id)
    assert task["status"] == "todo"
    assert task["watcher_ids"] == [str(watcher.id)]
    assert task["assignee_ids"] == [str(assignee.id)]

    outbox_event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.aggregate_id == task_id,
            OutboxEvent.event_type == "task.created",
        )
    )
    assert outbox_event is not None
    assert outbox_event.payload["title"] == payload["title"]
    assert outbox_event.payload["company_id"] == str(company_id)
    assert outbox_event.payload["assignee_ids"] == [str(assignee.id)]

    set_auth_token(company_id, role=MemberRoles.MEMBER, user_id=author.id)

    response = await client.post(f"/api/v1/companies/{company_id}/tasks", json=payload)
    assert response.status_code == 403
