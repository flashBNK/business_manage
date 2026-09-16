import uuid
from datetime import UTC, datetime

from infrastructure.databases.postgresql.models import UsersReplica


async def create_user(session, company_id: uuid.UUID, username: str = "Test User") -> UsersReplica:
    user = UsersReplica(
        id=uuid.uuid4(),
        username=username,
        company_id=company_id,
        is_active=True,
        last_event_at=datetime.now(UTC),
    )
    session.add(user)
    await session.commit()
    return user


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
