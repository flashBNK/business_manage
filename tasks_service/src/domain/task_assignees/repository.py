from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import AssigneesNotFound
from .models import CreateTaskAssigneesDTO, TaskAssigneesDTO


class AbstractTaskAssigneesRepository(AbstractRepository[TaskAssigneesDTO, UUID, CreateTaskAssigneesDTO], ABC):
    @abstractmethod
    async def list_by_task(self, task_id: UUID) -> list[TaskAssigneesDTO]:
        raise AssigneesNotFound

    @abstractmethod
    async def delete_by_list(self, assignee_ids: list[UUID]) -> None:
        raise AssigneesNotFound

    @abstractmethod
    async def delete_by_task(self, task_id: UUID) -> None:
        raise AssigneesNotFound
