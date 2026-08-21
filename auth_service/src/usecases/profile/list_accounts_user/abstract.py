import uuid
from abc import ABC, abstractmethod

from domain.account.models import AccountDTO


class AbstractListAccountsUserUseCase(ABC):
    @abstractmethod
    async def execute(self, user_id: uuid.UUID) -> tuple[list[AccountDTO], int]:
        ...