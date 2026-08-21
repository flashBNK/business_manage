from abc import ABC, abstractmethod

from domain.account.models import CreateAccountDTO, AccountDTO


class AbstractCheckAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateAccountDTO) -> None:
        ...
