from container import Container
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession


def build_unit_of_work(
    session: AsyncSession,
) -> PostgreSQLTasksUnitOfWork:
    return Container.uow_factory(session=session)
