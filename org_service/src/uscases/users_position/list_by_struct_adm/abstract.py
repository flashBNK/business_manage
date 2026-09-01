from abc import ABC, abstractmethod
from uuid import UUID

from domain.struct_adm.models import StructAdmDTO
from domain.users_position.models import EmployeePositionDTO


class AbstractListUsersPositionByStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(
        self, company_id: UUID, struct_adm_id, include_children: bool = False
    ) -> tuple[list[EmployeePositionDTO], StructAdmDTO]: ...
