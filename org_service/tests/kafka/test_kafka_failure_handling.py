from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from infrastructure.databases.postgresql.models.failed_message import FailedMessage, FailedMessageStatus
from infrastructure.databases.postgresql.models.inbox_event import InboxEvent
from infrastructure.kafka.consumer import consumer_loop
from infrastructure.repositories.postgresql.failed_message import PostgreSQLFailedMessageRepository
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_successful_message(session, session_manager, event, message, handler):
    consumer = AsyncMock()

    async def commit_message(message):
        inbox = await session.scalar(select(InboxEvent).where(InboxEvent.event_id == UUID(event["event_id"])))
        assert inbox is not None

    consumer.commit_message.side_effect = commit_message

    await consumer_loop.process_message(consumer, session_manager, message)
    await consumer_loop.process_message(consumer, session_manager, message)

    assert handler.await_count == 1
    assert consumer.commit_message.await_count == 2
    assert await session.scalar(select(FailedMessage)) is None


@pytest.mark.asyncio
async def test_failed_message_after_retry(session, session_manager, event, message, handler):
    handler.side_effect = RuntimeError("cannot create employee")
    consumer = AsyncMock()

    async def commit_message(message):
        failure = await session.scalar(select(FailedMessage).where(FailedMessage.offset == message.offset))
        assert failure is not None

    consumer.commit_message.side_effect = commit_message

    await consumer_loop.process_message(consumer, session_manager, message)

    failure = await session.scalar(select(FailedMessage))
    assert failure is not None
    assert failure.raw_value == message.value
    assert failure.raw_key == message.key
    assert failure.headers == [{"key": "trace", "value_base64": "dGVzdA=="}]
    assert failure.consumer_name == "org_service"
    assert failure.topic == message.topic
    assert failure.partition == message.partition
    assert failure.offset == message.offset
    assert failure.event_id == UUID(event["event_id"])
    assert failure.correlation_id == UUID(event["correlation_id"])
    assert failure.error_type == "RuntimeError"
    assert failure.error_message == "cannot create employee"
    assert failure.attempts == 3
    assert failure.status == FailedMessageStatus.PENDING
    assert handler.await_count == 3
    consumer.commit_message.assert_awaited_once_with(message)
    assert await session.scalar(select(InboxEvent)) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [b"not json", None])
async def test_invalid_message(session, session_manager, message, handler, value):
    message.value = value
    consumer = AsyncMock()

    async def commit_message(message):
        failure = await session.scalar(select(FailedMessage).where(FailedMessage.offset == message.offset))
        assert failure is not None

    consumer.commit_message.side_effect = commit_message

    await consumer_loop.process_message(consumer, session_manager, message)

    failure = await session.scalar(select(FailedMessage))
    assert failure is not None
    assert failure.raw_value == value
    assert failure.error_type
    assert failure.error_message
    assert failure.event_id is None
    assert failure.correlation_id is None
    assert failure.attempts == 0
    handler.assert_not_awaited()
    consumer.commit_message.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_failure_storage_error(session, session_manager, message, handler, monkeypatch):
    handler.side_effect = RuntimeError("cannot create employee")
    consumer = AsyncMock()
    monkeypatch.setattr(
        PostgreSQLFailedMessageRepository, "create", AsyncMock(side_effect=OSError("database unavailable"))
    )

    with pytest.raises(OSError, match="database unavailable"):
        await consumer_loop.process_message(consumer, session_manager, message)

    consumer.commit_message.assert_not_awaited()
    assert await session.scalar(select(FailedMessage)) is None
    assert await session.scalar(select(InboxEvent)) is None


@pytest.mark.asyncio
async def test_failed_message_redelivery(session, session_manager, message, handler):
    handler.side_effect = RuntimeError("cannot create employee")
    consumer = AsyncMock()
    consumer.commit_message.side_effect = OSError("offset commit failed")

    with pytest.raises(OSError, match="offset commit failed"):
        await consumer_loop.process_message(consumer, session_manager, message)

    assert await session.scalar(select(FailedMessage)) is not None
    consumer.commit_message.side_effect = None

    await consumer_loop.process_message(consumer, session_manager, message)

    assert handler.await_count == 3
    assert consumer.commit_message.await_count == 2
    assert await session.scalar(select(func.count()).select_from(FailedMessage)) == 1


@pytest.mark.asyncio
async def test_consumer_stops_after_error(session_manager, message, monkeypatch):
    consumer = AsyncMock()
    next_message = SimpleNamespace(topic=message.topic, partition=message.partition, offset=43)
    consumer.__aiter__.return_value = [message, next_message]
    process_message = AsyncMock(side_effect=OSError("database unavailable"))
    monkeypatch.setattr(consumer_loop, "process_message", process_message)

    with pytest.raises(OSError, match="database unavailable"):
        await consumer_loop.run_event_consumer(consumer, session_manager)

    assert process_message.await_count == 1
    consumer.commit_message.assert_not_awaited()
    consumer.stop.assert_awaited_once()
