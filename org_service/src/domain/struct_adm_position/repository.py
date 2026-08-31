from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import InvalidRequestStructAdmPosition
from .models import CreateStructAdmPositionDTO, StructAdmPositionDTO


class AbstractStructAdmPositionRepository(
    AbstractRepository[StructAdmPositionDTO, UUID, CreateStructAdmPositionDTO], ABC
):
    @abstractmethod
    async def list_by_struct_adm_id(self, struct_adm_id: UUID) -> list[StructAdmPositionDTO]:
        raise InvalidRequestStructAdmPosition
