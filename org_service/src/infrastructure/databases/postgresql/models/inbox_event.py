import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class InboxEvent(Base):
    __tablename__ = "inbox_event"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    consumer_name: Mapped[str] = mapped_column(String(127), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
