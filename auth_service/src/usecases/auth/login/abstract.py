from abc import ABC, abstractmethod

from domain.token.models import LoginDTO, LoginResultDTO


class AbstractLoginUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: LoginDTO) -> LoginResultDTO: ...
