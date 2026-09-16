import uuid
from datetime import UTC, datetime


def make_event(
    event_type: str,
    aggregate_id: uuid.UUID | None = None,
    correlation_id: uuid.UUID | None = None,
    payload: dict | None = None,
) -> dict:
    event_id = uuid.uuid4()

    return {
        "event_id": str(event_id),
        "event_type": event_type,
        "schema_version": 1,
        "aggregate_id": str(aggregate_id or uuid.uuid4()),
        "correlation_id": str(correlation_id or uuid.uuid4()),
        "causation_id": None,
        "producer": "auth_service",
        "occurred_at": datetime.now(UTC).isoformat(),
        "payload": payload or {},
    }
