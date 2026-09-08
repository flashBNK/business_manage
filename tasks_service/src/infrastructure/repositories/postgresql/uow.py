from infrastructure.repositories.postgresql.inbox_event import PostgreSQLInboxEventRepository
from infrastructure.repositories.postgresql.task import PostgreSQLTaskRepository
from infrastructure.repositories.postgresql.task_assignees import PostgreSQLTaskAssigneesRepository
from infrastructure.repositories.postgresql.task_watchers import PostgreSQLTaskWatcherRepository
from infrastructure.repositories.postgresql.users_replica import PostgreSQLUsersReplicaRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLTasksUnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

        self.users_replica: PostgreSQLUsersReplicaRepository | None = None
        self.inbox_event: PostgreSQLInboxEventRepository | None = None
        self.task: PostgreSQLTaskRepository | None = None
        self.task_watcher: PostgreSQLTaskWatcherRepository | None = None
        self.task_assignees: PostgreSQLTaskAssigneesRepository | None = None

    async def __aenter__(self):
        self.users_replica = PostgreSQLUsersReplicaRepository(session=self._session)
        self.inbox_event = PostgreSQLInboxEventRepository(session=self._session)
        self.task = PostgreSQLTaskRepository(session=self._session)
        self.task_watcher = PostgreSQLTaskWatcherRepository(session=self._session)
        self.task_assignees = PostgreSQLTaskAssigneesRepository(session=self._session)

        return self

    async def __aexit__(self, exc_type: Exception | None, exc_val, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
        self.users_replica = None
        self.inbox_event = None
        self.task = None
        self.task_watcher = None
        self.task_assignees = None

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
