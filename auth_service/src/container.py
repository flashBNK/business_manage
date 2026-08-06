from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, Factory

from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork


class Container(DeclarativeContainer):
    uow_factory = Factory(PostgreSQLUnitOfWork)

    session_manager = Singleton(DatabaseSessionManager)