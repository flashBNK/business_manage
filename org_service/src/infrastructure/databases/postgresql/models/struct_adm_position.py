import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class StructAdmPosition(Base):
    __tablename__ = "struct_adm_position"

    struct_adm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("struct_adm.id", ondelete="CASCADE"), primary_key=True
    )

    position_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("position.id", ondelete="CASCADE"), primary_key=True
    )