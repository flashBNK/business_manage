import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class OutboxEventType(enum.StrEnum):
    COMPANY_CREATED = "company.created"
    EMPLOYEE_CREATED = "employee.created"
    EMPLOYEE_REGISTERED = "employee.registered"
    EMPLOYEE_REGISTRATION_FAILED = "employee.registration.failed"

    REGISTRATION_ORG_PROVISION = "registration.org.provision"
    REGISTRATION_ORG_COMPLETED = "registration.org.completed"
    REGISTRATION_ORG_FAILED = "registration.org.failed"
    REGISTRATION_ORG_COMPENSATE = "registration.org.compensate"
    REGISTRATION_ORG_COMPENSATED = "registration.org.compensated"

    REGISTRATION_TASKS_PROVISION = "registration.tasks.provision"
    REGISTRATION_TASKS_COMPLETED = "registration.tasks.completed"
    REGISTRATION_TASKS_FAILED = "registration.tasks.failed"

    REGISTRATION_COMPLETED = "registration.completed"
    REGISTRATION_FAILED = "registration.failed"


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
    correlation_id: uuid.UUID | None = uuid.uuid4()
    causation_id: uuid.UUID | None = None
    schema_version: int = 1
