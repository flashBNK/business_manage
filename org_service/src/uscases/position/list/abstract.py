from abc import ABC, abstractmethod
from uuid import UUID

from domain.position.models import PositionDTO


class AbstractListPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID) -> list[PositionDTO]: ...
