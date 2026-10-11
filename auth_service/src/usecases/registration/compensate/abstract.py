from abc import ABC, abstractmethod
from uuid import UUID

from domain.registration_saga.models import RegistrationSagaDTO


class AbstractCompensateRegistrationUseCase(ABC):
    @abstractmethod
    async def execute(self, saga: RegistrationSagaDTO, reason: str, causation_id: UUID) -> None: ...
