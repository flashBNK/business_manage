from abc import ABC, abstractmethod
from uuid import UUID

from domain.users_position.models import GetUsersPositionDTO, UsersPositionDTO


class AbstractDeleteUsersPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: GetUsersPositionDTO, company_id: UUID) -> UsersPositionDTO: ...
