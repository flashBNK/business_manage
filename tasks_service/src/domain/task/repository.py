from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import TaskNotFound
from .models import ChangeStatusTaskDTO, CreateTaskDTO, TaskDTO, UpdateTaskDTO


class AbstractTaskRepository(AbstractRepository[TaskDTO, UUID, CreateTaskDTO], ABC):
    @abstractmethod
    async def list_by_company(self, company_id: UUID) -> list[TaskDTO]:
        raise TaskNotFound

    @abstractmethod
    async def update(self, dto: UpdateTaskDTO, task_id: UUID) -> TaskDTO:
        raise TaskNotFound

    @abstractmethod
    async def change_status(self, dto: ChangeStatusTaskDTO, task_id: UUID) -> TaskDTO:
        raise TaskNotFound
