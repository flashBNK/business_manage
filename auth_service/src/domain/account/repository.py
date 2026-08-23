from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository
from domain.account.exceptions import AccountNotFound

from .models import AccountDTO, CreateAccountDTO, UpdateAccountDTO


class AbstractAccountRepository(AbstractRepository[AccountDTO, UUID, CreateAccountDTO], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> AccountDTO:
        raise AccountNotFound

    @abstractmethod
    async def list_by_user_id(self, user_id: UUID) -> list[AccountDTO]:
        raise AccountNotFound

    @abstractmethod
    async def update(self, dto: UpdateAccountDTO, account_id: UUID) -> AccountDTO | None:
        raise AccountNotFound
