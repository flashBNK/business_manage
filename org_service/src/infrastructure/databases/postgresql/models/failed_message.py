import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, Enum, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import BYTEA, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class FailedMessageStatus(enum.StrEnum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISCARDED = "discarded"


class FailedMessage(Base):
    __tablename__ = "failed_message"

    __table_args__ = (
        UniqueConstraint("consumer_name", "topic", "partition", "offset", name="unique_failed_kafka_message"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    consumer_name: Mapped[str] = mapped_column(String(127), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    partition: Mapped[int] = mapped_column(Integer, nullable=False)
    offset: Mapped[int] = mapped_column(BigInteger, nullable=False)
    raw_value: Mapped[bytes | None] = mapped_column(BYTEA, nullable=True)
    raw_key: Mapped[bytes | None] = mapped_column(BYTEA, nullable=True)
    headers: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)
    event_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    correlation_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True, index=True)
    error_type: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[FailedMessageStatus] = mapped_column(
        Enum(FailedMessageStatus, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=FailedMessageStatus.PENDING,
        nullable=False,
        index=True,
    )
    failed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
