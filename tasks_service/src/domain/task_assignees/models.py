from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CreateTaskAssigneesDTO:
    task_id: UUID
    user_id: UUID


@dataclass(slots=True)
class TaskAssigneesDTO(CreateTaskAssigneesDTO):
    pass
