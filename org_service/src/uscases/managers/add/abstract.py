from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import AddManagerStructAdmDTO, ManagerDTO


class AbstractAddManagerStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: AddManagerStructAdmDTO, company_id: UUID) -> ManagerDTO: ...
