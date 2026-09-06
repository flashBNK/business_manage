import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class TaskAssignees(Base):
    __tablename__ = "task_assignees"

    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("task.id", ondelete="CASCADE"), primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users_replica.id", ondelete="CASCADE"), primary_key=True)
