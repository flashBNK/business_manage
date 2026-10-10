from datetime import datetime

from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from usecases.registration.recover.abstract import AbstractRecoverRegistrationSagasUseCase

TIMEOUT_ERRORS = {
    RegistrationStatus.STARTED: "org step timed out",
    RegistrationStatus.ORG_COMPLETED: "tasks step timed out",
    RegistrationStatus.TASKS_COMPLETED: "completion step timed out",
    RegistrationStatus.COMPENSATING: "compensation step timed out",
}


class PostgreSQLRecoverRegistrationSagasUseCase(AbstractRecoverRegistrationSagasUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, now: datetime) -> None:
        async with self._uow as uow:
            sagas = await uow.registration_saga.get_expired(now=now)

            for saga in sagas:
                await uow.registration_saga.mark_timeout(saga_id=saga.id, last_error=TIMEOUT_ERRORS[saga.status])
