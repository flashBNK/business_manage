from abc import ABC, abstractmethod
from uuid import UUID


from domain.abstract import AbstractRepository
from .models import UserDTO, CreateUserDTO


class AbstractUserRepository(AbstractRepository[UserDTO, UUID, CreateUserDTO], ABC):
    pass

    # @abstractmethod
    # async def find_by_filters(self, user_filters: UserFilterDTO) -> List[UserDTO]:
    #     raise UserNotFound