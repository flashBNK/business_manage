from datetime import UTC, datetime
from uuid import UUID

from domain.task.exceptions import TaskNotFound
from domain.task.models import ChangeStatusTaskDTO, CreateTaskDTO, TaskDTO, UpdateTaskDTO
from domain.task.repository import AbstractTaskRepository
from infrastructure.databases.postgresql.models.task import Task as TaskModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLTaskRepository(AbstractTaskRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateTaskDTO) -> TaskDTO:
        db_task = TaskModel(
            title=dto.title,
            description=dto.description,
            deadline=dto.deadline,
            estimated_minutes=dto.estimated_minutes,
            author_id=dto.author_id,
            responsible_id=dto.responsible_id,
            company_id=dto.company_id,
        )

        self._session.add(db_task)
        await self._session.flush()

        return self._to_domain(db_task)

    async def delete(self, task_id: UUID) -> None:
        stmt = self._active_query().where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise TaskNotFound

        task.deleted_at = datetime.now(UTC)

    async def get(self, task_id: UUID) -> TaskDTO | None:
        stmt = self._active_query().where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return None

        return self._to_domain(task)

    async def list_by_company(self, company_id: UUID) -> list[TaskDTO]:
        stmt = self._active_query().where(TaskModel.company_id == company_id)
        result = await self._session.execute(stmt)
        tasks = result.scalars().all()

        if not tasks:
            return []

        return [self._to_domain(task) for task in tasks]

    async def update(self, dto: UpdateTaskDTO, task_id: UUID) -> TaskDTO:
        stmt = self._active_query().where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise TaskNotFound

        if dto.title is not None:
            task.title = dto.title
        if dto.description is not None:
            task.description = dto.description
        if dto.deadline is not None:
            task.deadline = dto.deadline
        if dto.estimated_minutes is not None:
            task.estimated_minutes = dto.estimated_minutes
        if dto.responsible_id is not None:
            task.responsible_id = dto.responsible_id

        self._session.add(task)
        await self._session.flush()

        return self._to_domain(task)

    async def change_status(self, dto: ChangeStatusTaskDTO, task_id: UUID) -> TaskDTO:
        stmt = self._active_query().where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            raise TaskNotFound

        if task.status != dto.status:
            task.status = dto.status

        self._session.add(task)
        await self._session.flush()

        return self._to_domain(task)

    @staticmethod
    def _active_query():
        return select(TaskModel).where(TaskModel.deleted_at.is_(None))

    @staticmethod
    def _to_domain(db_task: TaskModel) -> TaskDTO:
        return TaskDTO(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            deadline=db_task.deadline,
            estimated_minutes=db_task.estimated_minutes,
            author_id=db_task.author_id,
            responsible_id=db_task.responsible_id,
            company_id=db_task.company_id,
            status=db_task.status,
            deleted_at=db_task.deleted_at,
        )
