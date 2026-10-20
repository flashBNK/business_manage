import asyncio
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from app import app
from domain.idempotency.models import SavedResponseDTO
from domain.task.models import ResponseTaskDTO, TaskDTO
from infrastructure.databases.postgresql.models.idempotency_request import IdempotencyRequest
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.task import Task, TaskStatus
from infrastructure.databases.postgresql.models.task_assignees import TaskAssignees
from infrastructure.databases.postgresql.models.task_watchers import TaskWatchers
from infrastructure.databases.postgresql.models.users_replica import UsersReplica
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.repositories.postgresql.idempotency_request import PostgreSQLIdempotencyRequestRepository
from pydantic import TypeAdapter
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..fixtures.factories import create_user


@pytest_asyncio.fixture()
async def task_request(client, session, engine, set_auth_token):
    company_id = uuid4()
    author = await create_user(session, company_id, "Author")
    responsible = await create_user(session, company_id, "Responsible")
    set_auth_token(company_id, user_id=author.id)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_request_session():
        async with factory() as request_session:
            yield request_session

    app.dependency_overrides[get_async_session] = get_request_session

    return (
        f"/api/v1/companies/{company_id}/tasks",
        {
            "title": "Test task",
            "description": "Description",
            "responsible_id": str(responsible.id),
            "deadline": None,
            "estimated_minutes": 30,
            "watcher_ids": [],
            "assignee_ids": [],
        },
        {"Idempotency-Key": "create-task-1"},
    )


async def assert_effect_count(session, count):
    assert await session.scalar(select(func.count()).select_from(Task)) == count
    assert await session.scalar(select(func.count()).select_from(IdempotencyRequest)) == count
    assert (
        await session.scalar(
            select(func.count()).select_from(OutboxEvent).where(OutboxEvent.event_type == "task.created")
        )
        == count
    )


@pytest.mark.asyncio
async def test_same_key_returns_saved_response(client, session, task_request):
    url, payload, headers = task_request
    first = await client.post(url, json=payload, headers=headers)
    assert first.status_code == 201

    await session.execute(update(Task).where(Task.id == UUID(first.json()["id"])).values(title="Renamed task"))
    await session.commit()

    second = await client.post(url, json=dict(reversed(payload.items())), headers=headers)

    assert second.status_code == 201
    assert first.json() == second.json()
    await assert_effect_count(session, 1)


@pytest.mark.asyncio
async def test_same_key_with_different_body_returns_conflict(client, session, task_request):
    url, payload, headers = task_request
    first = await client.post(url, json=payload, headers=headers)
    second = await client.post(url, json={**payload, "title": "Other task"}, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 409
    await assert_effect_count(session, 1)


@pytest.mark.asyncio
async def test_parallel_requests_create_one_task(client, session, task_request):
    url, payload, headers = task_request
    first, second = await asyncio.gather(
        client.post(url, json=payload, headers=headers),
        client.post(url, json=payload, headers=headers),
        return_exceptions=True,
    )

    assert not isinstance(first, BaseException), repr(first)
    assert not isinstance(second, BaseException), repr(second)
    assert first.status_code == second.status_code == 201
    assert first.json() == second.json()
    await assert_effect_count(session, 1)


@pytest.mark.asyncio
async def test_parallel_requests_with_different_bodies_return_conflict(client, session, task_request):
    url, payload, headers = task_request
    responses = await asyncio.gather(
        client.post(url, json=payload, headers=headers),
        client.post(url, json={**payload, "title": "Other task"}, headers=headers),
        return_exceptions=True,
    )

    for response in responses:
        assert not isinstance(response, BaseException), repr(response)
    assert sorted(response.status_code for response in responses) == [201, 409]
    await assert_effect_count(session, 1)


@pytest.mark.asyncio
async def test_different_keys_create_different_tasks(client, session, task_request):
    url, payload, headers = task_request
    first = await client.post(url, json=payload, headers=headers)
    second = await client.post(url, json=payload, headers={"Idempotency-Key": "create-task-2"})

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    await assert_effect_count(session, 2)


@pytest.mark.asyncio
async def test_failed_request_does_not_reserve_key(client, session, task_request):
    url, payload, headers = task_request
    failed = await client.post(url, json={**payload, "responsible_id": str(uuid4())}, headers=headers)

    assert failed.status_code == 404
    await assert_effect_count(session, 0)

    successful = await client.post(url, json=payload, headers=headers)

    assert successful.status_code == 201
    await assert_effect_count(session, 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("participant_count", [0, 1, 2])
async def test_create_without_key_preserves_participants(client, session, task_request, participant_count):
    url, payload, _ = task_request
    users = (await session.scalars(select(UsersReplica.id).order_by(UsersReplica.id))).all()
    participants = [str(user_id) for user_id in users[:participant_count]]
    payload = {**payload, "watcher_ids": participants, "assignee_ids": participants}

    response = await client.post(url, json=payload)

    assert response.status_code == 201
    assert response.json()["watcher_ids"] == participants
    assert response.json()["assignee_ids"] == participants
    assert await session.scalar(select(func.count()).select_from(TaskWatchers)) == participant_count
    assert await session.scalar(select(func.count()).select_from(TaskAssignees)) == participant_count
    assert await session.scalar(select(func.count()).select_from(IdempotencyRequest)) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("key", ["", "x" * 256])
async def test_invalid_key_is_rejected(client, session, task_request, key):
    url, payload, _ = task_request

    response = await client.post(url, json=payload, headers={"Idempotency-Key": key})

    assert response.status_code == 422
    await assert_effect_count(session, 0)


@pytest.mark.asyncio
async def test_repository_stores_typed_response(session):
    user_id = uuid4()
    task = TaskDTO(
        id=uuid4(),
        title="Saved task",
        description="Description",
        status=TaskStatus.TODO,
        author_id=user_id,
        responsible_id=user_id,
        company_id=uuid4(),
        deadline=None,
        estimated_minutes=30,
    )
    body = ResponseTaskDTO(task=task, watcher_ids=[], assignee_ids=[])
    response = SavedResponseDTO(status_code=201, body=body)
    session.add(IdempotencyRequest(scope="test", key="key", request_hash="hash"))
    await session.commit()

    repository = PostgreSQLIdempotencyRequestRepository(session)
    await repository.complete("test", "key", response)
    await session.commit()
    saved = await repository.get("test", "key")

    assert saved.response_status == 201
    assert saved.response_body == TypeAdapter(ResponseTaskDTO).dump_python(body, mode="json")
