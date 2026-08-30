from abc import ABC, abstractmethod

from domain.position.models import CreatePositionDTO, PositionDTO


class AbstractCreatePositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreatePositionDTO) -> PositionDTO: ...
