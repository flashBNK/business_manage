import uuid

from sqlalchemy import Text, String, UUID, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Position(Base):
    __tablename__ = "position"

    __table_args__ = (
        UniqueConstraint("company_id", "name", name="unique_position_company",),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)