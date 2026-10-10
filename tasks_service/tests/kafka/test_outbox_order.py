from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.repositories.postgresql.outbox_event import PostgreSQLOutboxEventRepository


@pytest.mark.asyncio
async def test_next_event_waits_until_previous_is_published(session, session_manager):
    task_id = uuid4()
    occurred_at = datetime(2026, 1, 1, tzinfo=UTC)
    created = OutboxEvent(
        aggregate_id=task_id,
        correlation_id=uuid4(),
        event_type="task.created",
        dedup_key="created",
        occurred_at=occurred_at,
    )
    updated = OutboxEvent(
        aggregate_id=task_id,
        correlation_id=created.correlation_id,
        event_type="task.updated",
        dedup_key="updated",
        occurred_at=occurred_at + timedelta(seconds=1),
    )
    session.add_all([created, updated])
    await session.commit()

    async with session_manager.session() as first_session, session_manager.session() as second_session:
        first_repo = PostgreSQLOutboxEventRepository(first_session)
        second_repo = PostgreSQLOutboxEventRepository(second_session)

        events = await first_repo.get_unpublished(limit=1)
        assert [event.event_id for event in events] == [created.event_id]
        assert await second_repo.get_unpublished(limit=1) == []

        await first_session.rollback()
        events = await second_repo.get_unpublished()
        assert [event.event_id for event in events] == [created.event_id]

        await second_repo.mark_published(created.event_id)
        await second_session.commit()

        events = await first_repo.get_unpublished()
        assert [event.event_id for event in events] == [updated.event_id]
