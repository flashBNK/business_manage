import enum
from datetime import UTC, datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class MemberRoles(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Members(Base):
    __tablename__ = "members"

    __table_args__ = (UniqueConstraint("user_id", "company_id", name="unique_user_in_company"),)


    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("company.id", ondelete="CASCADE"))
    role: Mapped[MemberRoles] = mapped_column(Enum(MemberRoles, values_callable=lambda x: [e.value for e in x], native_enum=False), default=MemberRoles.MEMBER)
    invite_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("invite.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))