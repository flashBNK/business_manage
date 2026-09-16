from uuid import UUID, uuid4

import pytest
from domain.token.models import MemberRoles
from infrastructure.databases.postgresql.models import OutboxEvent
from infrastructure.databases.postgresql.models.task import Task
from infrastructure.databases.postgresql.models.task_assignees import TaskAssignees
from infrastructure.databases.postgresql.models.task_watchers import TaskWatchers
from sqlalchemy import select

from ..fixtures.factories import create_user


@pytest.mark.asyncio
async def test_delete_task(client, session, set_auth_token):
    company_id = uuid4()
    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")
    watcher = await create_user(session, company_id, "Watcher")
    assignee = await create_user(session, company_id, "Assignee")

    set_auth_token(company_id, role=MemberRoles.ADMIN, user_id=author.id)

    create_response = await client.post(
        f"/api/v1/companies/{company_id}/tasks",
        json={
            "title": "Task to delete",
            "description": "Description",
            "responsible_id": str(responsible.id),
            "deadline": None,
            "estimated_minutes": 30,
            "watcher_ids": [str(watcher.id)],
            "assignee_ids": [str(assignee.id)],
        },
    )
    assert create_response.status_code == 201

    task_id = UUID(create_response.json()["id"])
    response = await client.delete(f"/api/v1/companies/{company_id}/tasks/{task_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/companies/{company_id}/tasks/{task_id}")
    assert response.status_code == 404

    response = await client.get(f"/api/v1/companies/{company_id}/tasks")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["tasks"] == []

    task = await session.scalar(select(Task).where(Task.id == task_id))
    assert task is not None
    assert task.deleted_at is not None

    watchers = (await session.scalars(select(TaskWatchers).where(TaskWatchers.task_id == task_id))).all()
    assignees = (await session.scalars(select(TaskAssignees).where(TaskAssignees.task_id == task_id))).all()
    assert watchers == []
    assert assignees == []

    event = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.aggregate_id == task_id,
            OutboxEvent.event_type == "task.deleted",
        )
    )

    assert event is not None
