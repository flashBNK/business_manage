from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import DeleteManagerStructAdmDTO, ManagerDTO


class AbstractDeleteManagerStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: DeleteManagerStructAdmDTO, company_id: UUID) -> ManagerDTO: ...
