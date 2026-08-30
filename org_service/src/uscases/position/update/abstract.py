from abc import ABC, abstractmethod
from uuid import UUID

from domain.position.models import PositionDTO, UpdatePositionDTO


class AbstractUpdatePositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: UpdatePositionDTO, company_id: UUID, position_id: UUID) -> PositionDTO: ...
