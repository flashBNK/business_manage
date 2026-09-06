import uuid
from datetime import UTC, datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_replica.id"), nullable=False, index=True)
    responsible_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_replica.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="todo")
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
