import uuid
from dataclasses import dataclass
from datetime import datetime

from infrastructure.databases.postgresql.models.failed_message import FailedMessageStatus


@dataclass(slots=True)
class FailedMessageDTO:
    id: uuid.UUID
    consumer_name: str
    topic: str
    partition: int
    offset: int
    headers: list[dict]
    error_type: str
    error_message: str
    attempts: int
    status: FailedMessageStatus
    failed_at: datetime
    raw_key: bytes | None = None
    raw_value: bytes | None = None
    event_id: uuid.UUID | None = None
    correlation_id: uuid.UUID | None = None
    resolved_at: datetime | None = None


@dataclass(slots=True)
class CreateFailedMessageDTO:
    consumer_name: str
    topic: str
    partition: int
    offset: int
    headers: list[dict]
    error_type: str
    error_message: str
    attempts: int
    status: FailedMessageStatus
    raw_key: bytes | None = None
    raw_value: bytes | None = None
    event_id: uuid.UUID | None = None
    correlation_id: uuid.UUID | None = None
