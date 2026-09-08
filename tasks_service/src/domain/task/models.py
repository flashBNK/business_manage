from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from infrastructure.databases.postgresql.models.task import TaskStatus


@dataclass(slots=True)
class CreateTaskDTO:
    title: str
    description: str
    deadline: datetime
    responsible_id: UUID
    author_id: UUID
    company_id: UUID
    estimated_minutes: int
    watcher_ids: list[UUID]
    assignee_ids: list[UUID]


@dataclass(slots=True)
class TaskDTO:
    id: UUID
    title: str
    description: str
    status: TaskStatus
    author_id: UUID
    responsible_id: UUID
    company_id: UUID
    deadline: datetime
    estimated_minutes: int
    deleted_at: datetime | None = None


@dataclass(slots=True)
class ResponseTaskDTO:
    task: TaskDTO
    watcher_ids: list[UUID]
    assignee_ids: list[UUID]


@dataclass(slots=True)
class UpdateTaskDTO:
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    estimated_minutes: int | None = None
    responsible_id: UUID | None = None
    watcher_ids: list[UUID] | None = None
    assignee_ids: list[UUID] | None = None


@dataclass(slots=True)
class ChangeStatusTaskDTO:
    status: TaskStatus