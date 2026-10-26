from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm_position.models import ListResponseStructAdmPositionDTO


class AbstractListStructAdmPositionUseCase(ABC):
    @abstractmethod
    async def execute(
        self, company_id: UUID, struct_adm_id: UUID, limit: int, offset: int
    ) -> ListResponseStructAdmPositionDTO: ...
