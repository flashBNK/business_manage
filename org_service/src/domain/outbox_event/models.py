import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class OutboxEventType(enum.StrEnum):
    STRUCT_ADM_CREATED = "struct_adm.created"
    STRUCT_ADM_UPDATED = "struct_adm.updated"
    STRUCT_ADM_DELETED = "struct_adm.deleted"
    EMPLOYEE_POSITION_CHANGED = "employee.position_changed"
    EMPLOYEE_POSITION_DELETED = "employee.position_deleted"
    POSITION_CREATED = "position.created"
    POSITION_UPDATED = "position.updated"
    POSITION_DELETED = "position.deleted"


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
