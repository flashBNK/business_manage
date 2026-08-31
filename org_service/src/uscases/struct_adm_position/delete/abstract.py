from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm_position.models import StructAdmPositionDTO


class AbstractDeleteStructAdmPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: StructAdmPositionDTO, company_id: UUID) -> None: ...
