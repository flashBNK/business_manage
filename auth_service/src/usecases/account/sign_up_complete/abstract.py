from abc import ABC, abstractmethod

from domain.account.models import CompleteSignUpDTO
from domain.token.models import LoginResultDTO


class AbstractCompleteSignUpUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CompleteSignUpDTO) -> LoginResultDTO:
        ...