from abc import ABC, abstractmethod


from domain.abstract import AbstractRepository
from .models import UserDTO, CreateUserDTO


class AbstractUserRepository(AbstractRepository[UserDTO, int, CreateUserDTO], ABC):
    pass

    # @abstractmethod
    # async def find_by_filters(self, user_filters: UserFilterDTO) -> List[UserDTO]:
    #     raise UserNotFound