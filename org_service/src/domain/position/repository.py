from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import PositionNotFound
from .models import CreatePositionDTO, PositionDTO, UpdatePositionDTO


class AbstractPositionRepository(AbstractRepository[PositionDTO, UUID, CreatePositionDTO], ABC):
    @abstractmethod
    async def list_paginated(self, company_id: UUID, limit: int, offset: int) -> tuple[list[PositionDTO], int]:
        raise PositionNotFound

    @abstractmethod
    async def update(self, position_id: UUID, dto=UpdatePositionDTO) -> PositionDTO | None:
        raise PositionNotFound
