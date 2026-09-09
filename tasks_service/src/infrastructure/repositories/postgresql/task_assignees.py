from uuid import UUID

from domain.task_assignees.models import CreateTaskAssigneesDTO, TaskAssigneesDTO
from domain.task_assignees.repository import AbstractTaskAssigneesRepository
from infrastructure.databases.postgresql.models.task_assignees import TaskAssignees as TaskAssigneesModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLTaskAssigneesRepository(AbstractTaskAssigneesRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateTaskAssigneesDTO) -> TaskAssigneesDTO:
        db_task_assignees = TaskAssigneesModel(
            user_id=dto.user_id,
            task_id=dto.task_id,
        )

        self._session.add(db_task_assignees)
        await self._session.flush()

        return self._to_domain(db_task_assignees)

    async def delete(self, user_id: UUID) -> None:
        pass

    async def get(self, task_id: UUID) -> TaskAssigneesDTO | None:
        stmt = select(TaskAssigneesModel).where(TaskAssigneesModel.task_id == task_id)
        result = await self._session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        return self._to_domain(task)

    async def list_by_task(self, task_id: UUID) -> list[TaskAssigneesDTO]:
        stmt = select(TaskAssigneesModel).where(TaskAssigneesModel.task_id == task_id)
        result = await self._session.execute(stmt)
        assignees = result.scalars().all()

        if not assignees:
            return []

        return [self._to_domain(assignee) for assignee in assignees]

    async def delete_by_list(self, assignee_ids: list[UUID]) -> None:
        stmt = delete(TaskAssigneesModel).where(TaskAssigneesModel.user_id.in_(assignee_ids))
        await self._session.execute(stmt)
        await self._session.flush()

    async def create_many(self, watcher_ids: list[UUID], task_id: UUID) -> list[TaskAssigneesDTO]:
        assignees = [TaskAssigneesModel(task_id=task_id, user_id=watcher_id) for watcher_id in watcher_ids]
        self._session.add_all(assignees)
        await self._session.flush()
        return [self._to_domain(assignee_id) for assignee_id in assignees]

    async def delete_by_task(self, task_id: UUID) -> None:
        stmt = delete(TaskAssigneesModel).where(TaskAssigneesModel.task_id == task_id)
        await self._session.execute(stmt)
        await self._session.flush()

    @staticmethod
    def _to_domain(db_task_assignees: TaskAssigneesModel) -> TaskAssigneesDTO:
        return TaskAssigneesDTO(
            task_id=db_task_assignees.task_id,
            user_id=db_task_assignees.user_id,
        )
