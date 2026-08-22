from abc import ABC, abstractmethod

from domain.token.models import LoginResultDTO


class AbstractRefreshUseCase(ABC):
    @abstractmethod
    async def execute(self, refresh_token: str) -> LoginResultDTO:
        ...
