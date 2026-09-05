import hashlib
import json
import uuid

from domain.outbox_event.models import OutboxEventType


def compute_dedup_key(event_type: OutboxEventType, aggregate_id: uuid.UUID, payload: dict) -> str:
    payload_repr = json.dumps(payload, sort_keys=True, default=str)
    raw = f"{event_type.value}:{aggregate_id}:{payload_repr}"
    return hashlib.sha256(raw.encode()).hexdigest()
