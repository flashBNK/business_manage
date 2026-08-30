from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import CreateStructAdmDTO, StructAdmDTO


class AbstractCreateStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateStructAdmDTO, parent_id: UUID) -> StructAdmDTO: ...
