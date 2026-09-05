import enum
import uuid

from sqlalchemy import Enum, ForeignKey, ForeignKeyConstraint, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Role(enum.StrEnum):
    MEMBER = "member"
    MANAGER = "manager"


class UsersPosition(Base):
    __tablename__ = "users_position"

    __table_args__ = (
        ForeignKeyConstraint(
            ["struct_adm_id", "position_id"],
            ["struct_adm_position.struct_adm_id", "struct_adm_position.position_id"],
            ondelete="RESTRICT",
        ),
        Index(
            "uq_users_position_one_manager_struct",
            "struct_adm_id",
            unique=True,
            postgresql_where=text("role = 'manager'"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_replica.id", ondelete="CASCADE"), primary_key=True)
    position_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("position.id"), primary_key=True)
    struct_adm_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("struct_adm.id"), primary_key=True)
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=Role.MEMBER,
    )
