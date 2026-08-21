from abc import ABC, abstractmethod

from domain.account.models import ConfirmAccountDTO, AccountDTO


class AbstractConfirmAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: ConfirmAccountDTO) -> AccountDTO:
        ...
