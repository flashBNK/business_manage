from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import CompanyStructureDTO


class AbstractGetCompanyStructureUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID) -> CompanyStructureDTO: ...
