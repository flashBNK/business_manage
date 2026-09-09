from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import WatcherNotFound
from .models import CreateTaskWatcherDTO, TaskWatcherDTO


class AbstractTaskWatcherRepository(AbstractRepository[TaskWatcherDTO, UUID, CreateTaskWatcherDTO], ABC):
    @abstractmethod
    async def list_by_task(self, task_id: UUID) -> list[TaskWatcherDTO]:
        raise WatcherNotFound

    @abstractmethod
    async def delete_by_list(self, watcher_ids: list[UUID]) -> None:
        raise WatcherNotFound

    @abstractmethod
    async def create_many(self, watcher_ids: list[UUID], task_id: UUID) -> None:
        raise WatcherNotFound

    @abstractmethod
    async def delete_by_task(self, task_id: UUID) -> None:
        raise WatcherNotFound
