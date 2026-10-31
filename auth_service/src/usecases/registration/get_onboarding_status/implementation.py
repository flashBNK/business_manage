from uuid import UUID

from domain.registration_saga.exceptions import RegistrationSagaNotFound
from domain.registration_saga.models import RegistrationSagaDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork

from .abstract import AbstractGetOnboardingStatusUseCase


class PostgreSQLGetOnboardingStatusUseCase(AbstractGetOnboardingStatusUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork):
        self._uow = uow

    async def execute(self, user_id: UUID, company_id: UUID) -> RegistrationSagaDTO:
        async with self._uow as uow:
            saga = await uow.registration_saga.get_latest(user_id=user_id, company_id=company_id)

            if saga is None:
                raise RegistrationSagaNotFound

            return saga