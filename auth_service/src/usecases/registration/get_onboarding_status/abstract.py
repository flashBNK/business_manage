from abc import ABC, abstractmethod
from uuid import UUID

from domain.registration_saga.models import RegistrationSagaDTO


class AbstractGetOnboardingStatusUseCase(ABC):
    @abstractmethod
    async def execute(self, user_id: UUID, company_id: UUID) -> RegistrationSagaDTO:
        raise NotImplementedError