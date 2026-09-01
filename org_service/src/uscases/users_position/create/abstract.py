from abc import ABC, abstractmethod
from uuid import UUID

from domain.users_position.models import CreateUsersPositionDTO, UsersPositionDTO


class AbstractCreateUsersPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateUsersPositionDTO, company_id: UUID) -> UsersPositionDTO: ...
