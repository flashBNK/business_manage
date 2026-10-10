import asyncio
from datetime import UTC, datetime

from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from logger import get_logger
from usecases.registration.recover.implementation import PostgreSQLRecoverRegistrationSagasUseCase

log = get_logger(__name__)


async def run_saga_recovery(session_manager: DatabaseSessionManager) -> None:
    while True:
        try:
            async with session_manager.session() as session:
                uow = PostgreSQLAuthUnitOfWork(session=session)
                usecase = PostgreSQLRecoverRegistrationSagasUseCase(uow=uow)

                await usecase.execute(now=datetime.now(UTC))

        except Exception:
            log.exception("Ошибка проверки просроченных саг")

        await asyncio.sleep(5)
