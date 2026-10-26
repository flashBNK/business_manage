from abc import ABC, abstractmethod
from uuid import UUID

from domain.task.models import ListResponseTaskDTO


class AbstractListTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, limit: int, offset: int) -> ListResponseTaskDTO: ...
