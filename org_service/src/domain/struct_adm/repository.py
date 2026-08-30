from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import StructAdmNotFound
from .models import CreateStructAdmDTO, StructAdmDTO, UpdateStructAdmDTO


class AbstractStructAdmRepository(AbstractRepository[StructAdmDTO, UUID, CreateStructAdmDTO], ABC):
    @abstractmethod
    async def ensure_root(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        raise StructAdmNotFound

    @abstractmethod
    async def get_children(self, parent_path: str) -> list[StructAdmDTO]:
        raise StructAdmNotFound

    @abstractmethod
    async def get_descendants(self, parent_path: str) -> list[StructAdmDTO]:
        raise StructAdmNotFound

    @abstractmethod
    async def get_ancestors(self, struct_adm_path: str) -> list[StructAdmDTO]:
        raise StructAdmNotFound

    @abstractmethod
    async def update(self, struct_adm_id: UUID, dto: UpdateStructAdmDTO) -> StructAdmDTO:
        raise StructAdmNotFound

    @abstractmethod
    async def move_subtree(self, old_path: str, new_path: str) -> None:
        raise StructAdmNotFound
