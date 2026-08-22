from abc import ABC, abstractmethod

from domain.account.models import AccountDTO, ConfirmEmailChangeDTO


class AbstractConfirmUpdateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: ConfirmEmailChangeDTO) -> AccountDTO:
        ...