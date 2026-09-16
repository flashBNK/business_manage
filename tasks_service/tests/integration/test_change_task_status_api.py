from uuid import UUID, uuid4

import pytest
from domain.token.models import MemberRoles
from infrastructure.databases.postgresql.models import OutboxEvent
from infrastructure.databases.postgresql.models.task import TaskStatus
from sqlalchemy import select

from ..fixtures.factories import create_user


@pytest.mark.asyncio
async def test_change_task_status(client, session, set_auth_token):
    company_id = uuid4()

    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")

    set_auth_token(company_id, role=MemberRoles.ADMIN, user_id=author.id)

    create_response = await client.post(
        f"/api/v1/companies/{company_id}/tasks",
        json={
            "title": "Task",
            "description": "Description",
            "responsible_id": str(responsible.id),
            "deadline": None,
            "estimated_minutes": 30,
            "watcher_ids": [],
            "assignee_ids": [str(responsible.id)],
        },
    )
    assert create_response.status_code == 201

    task_id = UUID(create_response.json()["id"])
    response = await client.patch(
        f"/api/v1/companies/{company_id}/tasks/{task_id}/change_status",
        json={"status": TaskStatus.IN_PROGRESS.value},
    )
    assert response.status_code == 200

    task = response.json()
    assert task["id"] == str(task_id)
    assert task["status"] == "in_progress"

    event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.aggregate_id == task_id,
            OutboxEvent.event_type == "task.status_changed",
        )
    )
    assert event is not None
    assert event.payload["old_status"] == "todo"
    assert event.payload["new_status"] == "in_progress"
