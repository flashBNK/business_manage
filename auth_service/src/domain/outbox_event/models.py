import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class OutboxEventType(enum.StrEnum):
    COMPANY_CREATED = "company.created"
    EMPLOYEE_CREATED = "employee.created"
    EMPLOYEE_REGISTERED = "employee.registered"
    EMPLOYEE_EMAIL_CHANGED = "employee.email_changed"


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
