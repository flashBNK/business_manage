import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class OutboxEventType(enum.StrEnum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_STATUS_CHANGED = "task.status_changed"


@dataclass(slots=True)
class OutboxEventDTO:
    event_id: uuid.UUID
    event_type: OutboxEventType
    aggregate_id: uuid.UUID
    correlation_id: uuid.UUID
    causation_id: uuid.UUID | None
    payload: dict
    schema_version: int
    dedup_key: str
    producer: str
    occurred_at: datetime
    published_at: datetime | None


@dataclass(slots=True)
class CreateOutboxEventDTO:
    event_type: OutboxEventType
    payload: dict
    aggregate_id: uuid.UUID
    correlation_id: uuid.UUID | None = None
    causation_id: uuid.UUID | None = None
    schema_version: int = 1
