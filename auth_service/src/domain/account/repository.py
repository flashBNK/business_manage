from abc import ABC, abstractmethod

from domain.account.exceptions import AccountNotFound
from domain.abstract import AbstractRepository
from .models import AccountDTO, CreateAccountDTO


class AbstractAccountRepository(AbstractRepository[AccountDTO, int, CreateAccountDTO], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> AccountDTO:
        raise AccountNotFound

    # @abstractmethod
    # async def find_by_filters(self, filters: FilterDTO) -> List[DTO]:
    #     raise NotFound