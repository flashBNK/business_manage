from abc import ABC, abstractmethod
from uuid import UUID

from domain.task.models import ResponseTaskDTO, UpdateTaskDTO


class AbstractUpdateTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: UpdateTaskDTO, company_id: UUID, task_id: UUID) -> ResponseTaskDTO: ...
