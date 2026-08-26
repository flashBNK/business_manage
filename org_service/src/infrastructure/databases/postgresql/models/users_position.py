import enum
import uuid

from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class Role(enum.StrEnum):
    MEMBER = "member"
    MANAGER = "manager"


class UsersPosition(Base):
    __tablename__ = "users_position"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users_replica.id", ondelete="CASCADE"), primary_key=True
    )
    position_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("position.id", ondelete="CASCADE"), primary_key=True
    )
    struct_adm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("struct_adm.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=Role.MEMBER,
    )