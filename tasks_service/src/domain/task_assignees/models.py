from uuid import UUID
from dataclasses import dataclass


@dataclass(slots=True)
class CreateTaskAssigneesDTO:
    task_id: UUID
    user_id: UUID


@dataclass(slots=True)
class TaskAssigneesDTO(CreateTaskAssigneesDTO):
    pass