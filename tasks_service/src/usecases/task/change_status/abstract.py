from abc import ABC, abstractmethod
from uuid import UUID

from domain.task.models import ChangeStatusTaskDTO, ResponseTaskDTO


class AbstractChangeStatusTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: ChangeStatusTaskDTO, company_id: UUID, task_id: UUID) -> ResponseTaskDTO: ...
