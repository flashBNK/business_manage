from abc import ABC, abstractmethod
from uuid import UUID

from domain.position.models import PositionDTO


class AbstractGetPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, position_id: UUID) -> PositionDTO: ...
