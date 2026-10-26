from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import StructAdmDTO
from domain.users_position.models import ListResponseEmployeePositionDTO


class AbstractListUsersPositionByStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(
        self, company_id: UUID, struct_adm_id: UUID, include_children: bool, limit: int, offset: int
    ) -> tuple[ListResponseEmployeePositionDTO, StructAdmDTO]: ...
