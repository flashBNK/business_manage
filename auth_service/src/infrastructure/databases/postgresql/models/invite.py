import enum
import uuid

from datetime import UTC, datetime
from sqlalchemy import DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Invite(Base):
    __tablename__ = "invite"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[InviteStatus] = mapped_column(Enum(InviteStatus, values_callable=lambda x: [e.value for e in x], native_enum=False), default=InviteStatus.PENDING)
    attempts: Mapped[int] = mapped_column(default=0)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
