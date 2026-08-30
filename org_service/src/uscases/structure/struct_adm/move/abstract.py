from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import MoveStructAdmDTO, StructAdmDTO


class AbstractMoveStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, struct_adm_id: UUID, company_id: UUID, dto: MoveStructAdmDTO) -> StructAdmDTO: ...
