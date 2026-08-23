from abc import ABC, abstractmethod

from domain.account.models import AccountDTO, ConfirmAccountDTO


class AbstractConfirmAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: ConfirmAccountDTO) -> AccountDTO: ...
