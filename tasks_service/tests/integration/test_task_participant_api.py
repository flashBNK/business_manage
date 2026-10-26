from contextlib import contextmanager
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import event

from ..fixtures.factories import create_user


@contextmanager
def capture_replica_selects(engine):
    statements = []

    def record(connection, cursor, statement, parameters, context, executemany):
        normalized = " ".join(statement.lower().split())

        if normalized.startswith("select") and "from users_replica" in normalized:
            statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", record)

    try:
        yield statements
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", record)


@pytest_asyncio.fixture()
async def participant_request(client, session, set_auth_token):
    company_id = uuid4()
    author = await create_user(session, company_id, "Author")

    set_auth_token(company_id, user_id=author.id)

    url = f"/api/v1/companies/{company_id}/tasks"
    base_payload = {
        "title": "Initial task",
        "description": "Description",
        "responsible_id": str(author.id),
        "deadline": None,
        "estimated_minutes": 30,
        "watcher_ids": [str(author.id)],
        "assignee_ids": [str(author.id)],
    }

    response = await client.post(url, json=base_payload)
    assert response.status_code == 201

    task_id = response.json()["id"]

    async def send(operation, changes):
        if operation == "create":
            return await client.post(url, json={**base_payload, **changes})

        return await client.patch(f"{url}/{task_id}", json=changes)

    return SimpleNamespace(company_id=company_id, author_id=author.id, send=send)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["create", "update"])
@pytest.mark.parametrize("participant_count", [1, 20])
async def test_participants_are_loaded_in_one_query(
    session, engine, participant_request, operation, participant_count
):
    context = participant_request

    users = [
        await create_user(session, context.company_id, f"Participant {index}") for index in range(participant_count)
    ]
    user_ids = [str(user.id) for user in users]

    with capture_replica_selects(engine) as statements:
        response = await context.send(
            operation,
            {
                "responsible_id": user_ids[0],
                "watcher_ids": user_ids,
                "assignee_ids": user_ids,
            },
        )

    expected_status = 201 if operation == "create" else 200

    assert response.status_code == expected_status
    assert len(statements) == 1

    task = response.json()

    assert task["responsible_id"] == user_ids[0]
    assert set(task["watcher_ids"]) == set(user_ids)
    assert set(task["assignee_ids"]) == set(user_ids)


@pytest.mark.asyncio
async def test_patch_preserves_or_clears_participants_without_lookup(engine, participant_request):
    context = participant_request
    author_ids = [str(context.author_id)]

    cases = [
        ({"title": "Renamed task"}, author_ids),
        ({"watcher_ids": [], "assignee_ids": []}, []),
    ]

    for changes, expected_ids in cases:
        with capture_replica_selects(engine) as statements:
            response = await context.send("update", changes)

        assert response.status_code == 200
        assert len(statements) == 0

        task = response.json()

        assert task["watcher_ids"] == expected_ids
        assert task["assignee_ids"] == expected_ids
