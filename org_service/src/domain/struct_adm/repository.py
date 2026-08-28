from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import StructAdmNotFound
from .models import CreateStructAdmDTO, StructAdmDTO


class AbstractStructAdmRepository(AbstractRepository[StructAdmDTO, UUID, CreateStructAdmDTO], ABC):
    @abstractmethod
    async def ensure_root(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        raise StructAdmNotFound
