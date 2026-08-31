from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm_position.models import CreateStructAdmPositionDTO, StructAdmPositionDTO


class AbstractCreateStructAdmPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateStructAdmPositionDTO, company_id: UUID) -> StructAdmPositionDTO: ...
