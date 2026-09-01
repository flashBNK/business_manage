from abc import ABC, abstractmethod
from uuid import UUID

from domain.users_position.models import (
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)


class AbstractUpdateUsersPositionUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: UpdateUsersPositionDTO, company_id: UUID) -> UsersPositionDTO: ...
