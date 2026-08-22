from abc import ABC, abstractmethod

class AbstractLogoutUseCase(ABC):
    @abstractmethod
    async def execute(self, refresh_token: str) -> None:
        ...
