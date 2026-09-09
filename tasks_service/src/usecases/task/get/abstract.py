from abc import ABC, abstractmethod
from uuid import UUID

from domain.task.models import ResponseTaskDTO


class AbstractGetTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, task_id: UUID) -> ResponseTaskDTO: ...
