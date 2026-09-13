import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class RegistrationStatus(enum.StrEnum):
    STARTED = "started"
    ORG_COMPLETED = "org_completed"
    TASKS_COMPLETED = "tasks_completed"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"


class RegistrationSaga(Base):
    __tablename__ = "registration_saga"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("company.id", ondelete="CASCADE"), index=True, nullable=False
    )
    invite_id: Mapped[uuid.UUID] = mapped_column(index=True, nullable=False, unique=True)
    correlation_id: Mapped[uuid.UUID] = mapped_column(nullable=False, unique=True, index=True)
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(
            RegistrationStatus,
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
        ),
        default=RegistrationStatus.STARTED,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
