from uuid import UUID
from dataclasses import dataclass


@dataclass(slots=True)
class CreateTaskWatcherDTO:
    task_id: UUID
    user_id: UUID


@dataclass(slots=True)
class TaskWatcherDTO(CreateTaskWatcherDTO):
    pass