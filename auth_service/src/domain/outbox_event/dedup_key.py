import hashlib
import json
from uuid import UUID

from domain.outbox_event.models import OutboxEventType


def compute_dedup_key(event_type: OutboxEventType, aggregate_id: UUID, payload: dict, correlation_id: UUID) -> str:
    payload_repr = json.dumps(payload, sort_keys=True, default=str)
    raw = f"{event_type.value}:{aggregate_id}:{payload_repr}:{correlation_id}"
    return hashlib.sha256(raw.encode()).hexdigest()
