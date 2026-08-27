import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class EventType(enum.StrEnum):
    COMPANY_CREATED = "company.created"
    EMPLOYEE_CREATED = "employee.created"
    EMPLOYEE_REGISTERED = "employee.registered"
    EMPLOYEE_EMAIL_CHANGED = "employee.email_changed"


@dataclass
class EventEnvelopeDTO:
    event_id: UUID
    event_type: EventType
    schema_version: int
    aggregate_id: UUID
    correlation_id: UUID
    causation_id: UUID | None
    producer: str
    occurred_at: datetime
    payload: dict

    @staticmethod
    def from_dict(data: dict) -> "EventEnvelopeDTO":
        return EventEnvelopeDTO(
            event_id=UUID(data["event_id"]),
            event_type=EventType(data["event_type"]),
            schema_version=data["schema_version"],
            aggregate_id=UUID(data["aggregate_id"]),
            correlation_id=UUID(data["correlation_id"]),
            causation_id=UUID(data["causation_id"]) if data["causation_id"] else None,
            producer=data["producer"],
            occurred_at=datetime.fromisoformat(data["occurred_at"]),
            payload=data["payload"],
        )
