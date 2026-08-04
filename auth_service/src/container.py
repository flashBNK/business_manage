from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager


class Container(DeclarativeContainer):
    """DI-контейнер auth_service."""

    # user_uow_factory = Factory(PostgreSQLUserUnitOfWork)

    session_manager = Singleton(DatabaseSessionManager)