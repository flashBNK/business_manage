import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class CompanyReplica(Base):
    __tablename__ = "company_replica"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
