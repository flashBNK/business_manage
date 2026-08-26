from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .models import CreateOutboxEventDTO, OutboxEventDTO


class AbstractOutboxEventRepository(AbstractRepository[OutboxEventDTO, UUID, CreateOutboxEventDTO], ABC):
    @abstractmethod
    def get_unpublished(self, limit: int = 100) -> list[OutboxEventDTO]:
        pass

    @abstractmethod
    async def mark_published(self, event_id: UUID) -> None:
        raise NotImplementedError
