from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import PositionNotFound
from .models import CreatePositionDTO, PositionDTO, UpdatePositionDTO


class AbstractPositionRepository(AbstractRepository[PositionDTO, UUID, CreatePositionDTO], ABC):
    @abstractmethod
    async def list(self, company_id: UUID) -> list[PositionDTO]:
        raise PositionNotFound

    @abstractmethod
    async def update(self, position_id: UUID, dto=UpdatePositionDTO) -> PositionDTO | None:
        raise PositionNotFound
