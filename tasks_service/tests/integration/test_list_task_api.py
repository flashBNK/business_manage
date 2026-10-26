from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from infrastructure.databases.postgresql.models.task import Task
from infrastructure.databases.postgresql.models.task_assignees import TaskAssignees
from infrastructure.databases.postgresql.models.task_watchers import TaskWatchers
from sqlalchemy import event

from ..fixtures.factories import create_user


@contextmanager
def capture_selects(engine):
    statements = []

    def record(
        connection,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(
        engine.sync_engine,
        "before_cursor_execute",
        record,
    )

    try:
        yield statements
    finally:
        event.remove(
            engine.sync_engine,
            "before_cursor_execute",
            record,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("page_size", [1, 20, 100])
async def test_task_page_loads_participants_in_batches(
    client,
    session,
    engine,
    set_auth_token,
    page_size,
):
    company_id = uuid4()
    other_company_id = uuid4()

    author = await create_user(session, company_id, "Author")
    watcher = await create_user(session, company_id, "Watcher")
    assignee = await create_user(session, company_id, "Assignee")
    other_user = await create_user(
        session,
        other_company_id,
        "Other company user",
    )

    now = datetime.now(UTC)

    common_values = {
        "description": "Description",
        "author_id": author.id,
        "responsible_id": author.id,
        "company_id": company_id,
        "estimated_minutes": 30,
    }

    tasks = [
        Task(
            id=uuid4(),
            title=f"Task {index}",
            created_at=now + timedelta(seconds=index),
            **common_values,
        )
        for index in range(page_size + 2)
    ]

    deleted_task = Task(
        id=uuid4(),
        title="Deleted task",
        created_at=now,
        deleted_at=now,
        **common_values,
    )

    other_task = Task(
        id=uuid4(),
        title="Other company task",
        description="Description",
        author_id=other_user.id,
        responsible_id=other_user.id,
        company_id=other_company_id,
        estimated_minutes=30,
        created_at=now,
    )

    session.add_all([*tasks, deleted_task, other_task])
    await session.flush()

    expected_participants = {}

    for index, task in enumerate(tasks):
        watcher_ids = [watcher.id] if index % 3 != 0 else []
        assignee_ids = [assignee.id, author.id] if index % 2 != 0 else []

        expected_participants[str(task.id)] = {
            "watchers": {str(user_id) for user_id in watcher_ids},
            "assignees": {str(user_id) for user_id in assignee_ids},
        }

        session.add_all([TaskWatchers(task_id=task.id, user_id=user_id) for user_id in watcher_ids])
        session.add_all([TaskAssignees(task_id=task.id, user_id=user_id) for user_id in assignee_ids])

    await session.commit()

    set_auth_token(company_id, user_id=author.id)

    url = f"/api/v1/companies/{company_id}/tasks"

    with capture_selects(engine) as statements:
        response = await client.get(url, params={"limit": page_size, "offset": 1})

    assert response.status_code == 200
    assert len(statements) == 4

    page = response.json()

    assert page["total"] == len(tasks)
    assert page["limit"] == page_size
    assert page["offset"] == 1
    assert len(page["tasks"]) == page_size

    expected_page = list(reversed(tasks))[1 : page_size + 1]

    assert [item["id"] for item in page["tasks"]] == [str(task.id) for task in expected_page]

    for item in page["tasks"]:
        expected = expected_participants[item["id"]]

        assert set(item["watcher_ids"]) == expected["watchers"]
        assert set(item["assignee_ids"]) == expected["assignees"]

    with capture_selects(engine) as statements:
        response = await client.get(url, params={"limit": page_size, "offset": 10_000})

    assert response.status_code == 200
    assert len(statements) == 2

    empty_page = response.json()

    assert empty_page["tasks"] == []
    assert empty_page["total"] == len(tasks)
    assert empty_page["limit"] == page_size
    assert empty_page["offset"] == 10_000
