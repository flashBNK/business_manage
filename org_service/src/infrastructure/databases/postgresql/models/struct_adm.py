import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import LtreeType

from ..base import Base


class StructAdm(Base):
    __tablename__ = "struct_adm"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("company_replica.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(LtreeType, nullable=False, unique=True)
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users_replica.id", ondelete="SET NULL"), nullable=True, index=True
    )
