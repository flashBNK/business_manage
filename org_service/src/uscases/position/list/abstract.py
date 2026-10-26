from abc import ABC, abstractmethod
from uuid import UUID

from domain.position.models import ListResponsePositionDTO


class AbstractListPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, limit: int, offset: int) -> ListResponsePositionDTO: ...
