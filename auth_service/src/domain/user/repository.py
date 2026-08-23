from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import UserNotFound
from .models import CreateUserDTO, UpdateUserDTO, UserDTO


class AbstractUserRepository(AbstractRepository[UserDTO, UUID, CreateUserDTO], ABC):
    @abstractmethod
    async def update(self, dto: UpdateUserDTO, user_id: UUID) -> UserDTO:
        raise UserNotFound
