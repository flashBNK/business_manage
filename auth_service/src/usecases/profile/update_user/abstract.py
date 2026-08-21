import uuid
from abc import ABC, abstractmethod

from domain.user.models import UpdateUserDTO, UserDTO


class AbstractUpdateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: UpdateUserDTO, user_id: uuid.UUID) -> UserDTO:
        ...