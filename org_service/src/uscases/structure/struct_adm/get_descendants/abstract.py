from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import StructAdmDTO


class AbstractGetDescendantsStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, parent_id: UUID, company_id: UUID) -> list[StructAdmDTO]: ...
