import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_event"

    event_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(127), nullable=False, unique=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    correlation_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    causation_id: Mapped[uuid.UUID | None] = mapped_column(default=None)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    dedup_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    producer: Mapped[str] = mapped_column(String(127), nullable=False, unique=False, default="auth_service")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
