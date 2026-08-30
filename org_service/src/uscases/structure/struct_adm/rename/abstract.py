from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import StructAdmDTO, UpdateStructAdmDTO


class AbstractRenameStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, struct_adm_id: UUID, company_id: UUID, dto: UpdateStructAdmDTO) -> StructAdmDTO: ...
