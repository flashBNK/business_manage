from datetime import datetime
from uuid import UUID

from infrastructure.databases.postgresql.models.task import TaskStatus
from pydantic import BaseModel


class TaskSchema(BaseModel):
    id: UUID
    title: str
    description: str
    status: TaskStatus
    author_id: UUID
    responsible_id: UUID
    company_id: UUID
    deadline: datetime | None = None
    estimated_minutes: int
    deleted_at: datetime | None = None
    watcher_ids: list[UUID]
    assignee_ids: list[UUID]


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    responsible_id: UUID
    deadline: datetime | None = None
    estimated_minutes: int
    watcher_ids: list[UUID]
    assignee_ids: list[UUID]


class ListTaskSchema(BaseModel):
    total: int
    tasks: list[TaskSchema]


class UpdateTaskSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    estimated_minutes: int | None = None
    responsible_id: UUID | None = None
    watcher_ids: list[UUID] | None = None
    assignee_ids: list[UUID] | None = None


class ChangeStatusTaskSchema(BaseModel):
    status: TaskStatus