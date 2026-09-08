from uuid import UUID

from domain.task_watchers.models import CreateTaskWatcherDTO, TaskWatcherDTO
from domain.task_watchers.repository import AbstractTaskWatcherRepository
from infrastructure.databases.postgresql.models.task_watchers import TaskWatchers as TaskWatchersModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLTaskWatcherRepository(AbstractTaskWatcherRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateTaskWatcherDTO) -> TaskWatcherDTO:
        db_task_watchers = TaskWatchersModel(
            user_id=dto.user_id,
            task_id=dto.task_id,
        )

        self._session.add(db_task_watchers)
        await self._session.flush()

        return self._to_domain(db_task_watchers)


    async def delete(self, user_id: UUID) -> None:
        pass


    async def get(self, task_id: UUID) -> TaskWatcherDTO | None:
        pass


    async def list_by_task(self, task_id: UUID) -> list[TaskWatcherDTO]:
        stmt = select(TaskWatchersModel).where(TaskWatchersModel.task_id == task_id)
        result = await self._session.execute(stmt)
        watchers = result.scalars().all()

        if not watchers:
            return []

        return [self._to_domain(watcher) for watcher in watchers]


    async def delete_by_list(self, watcher_ids: list[UUID]) -> None:
        stmt = delete(TaskWatchersModel.where(TaskWatchersModel.user_id.in_(watcher_ids)))
        await self._session.execute(stmt)
        await self._session.flush()


    async def create_many(self, watcher_ids: list[UUID], task_id: UUID) -> list[TaskWatcherDTO]:
        watchers = [TaskWatchersModel(task_id=task_id, user_id=watcher_id) for watcher_id in watcher_ids]
        self._session.add_all(watchers)
        await self._session.flush()
        return [self._to_domain(watcher_id) for watcher_id in watchers]


    async def delete_by_task(self, task_id: UUID) -> None:
        stmt = delete(TaskWatchersModel).where(TaskWatchersModel.task_id == task_id)
        await self._session.execute(stmt)
        await self._session.flush()


    @staticmethod
    def _to_domain(db_task_watchers: TaskWatchersModel) -> TaskWatcherDTO:
        return TaskWatcherDTO(
            task_id=db_task_watchers.task_id,
            user_id=db_task_watchers.user_id,
        )
