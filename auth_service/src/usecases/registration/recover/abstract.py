from abc import ABC, abstractmethod
from datetime import datetime


class AbstractRecoverRegistrationSagasUseCase(ABC):
    @abstractmethod
    async def execute(self, now: datetime) -> None: ...
