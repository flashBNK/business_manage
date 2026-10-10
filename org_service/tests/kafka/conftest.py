import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.consumer import consumer_loop, retry


@pytest_asyncio.fixture()
async def session_manager():
    manager = DatabaseSessionManager()
    manager.init(os.environ["DATABASE_URL"])
    yield manager
    await manager.close()


@pytest.fixture()
def event():
    return {
        "event_id": str(uuid4()),
        "event_type": "employee.registered",
        "schema_version": 1,
        "aggregate_id": str(uuid4()),
        "correlation_id": str(uuid4()),
        "causation_id": None,
        "producer": "auth_service",
        "occurred_at": "2026-01-01T00:00:00+00:00",
        "payload": {},
    }


@pytest.fixture()
def message(event):
    return SimpleNamespace(
        topic="auth.employee.events",
        partition=0,
        offset=42,
        value=json.dumps(event).encode(),
        key=b"employee",
        headers=[("trace", b"test")],
    )


@pytest.fixture()
def handler(monkeypatch):
    handler = AsyncMock()
    monkeypatch.setattr(consumer_loop, "EVENT_HANDLERS", {"employee.registered": handler})
    monkeypatch.setattr(retry.asyncio, "sleep", AsyncMock())
    return handler
