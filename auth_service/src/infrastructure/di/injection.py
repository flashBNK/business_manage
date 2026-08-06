from sqlalchemy.ext.asyncio import AsyncSession

from container import Container
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork


def build_unit_of_work(
    session: AsyncSession,
) -> PostgreSQLUnitOfWork:
    return Container.uow_factory(session=session)