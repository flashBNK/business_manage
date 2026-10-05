from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .models import CreateFailedMessageDTO, FailedMessageDTO


class AbstractFailedMessageRepository(AbstractRepository[FailedMessageDTO, UUID, CreateFailedMessageDTO], ABC):
    @abstractmethod
    async def get_by_source(
        self, consumer_name: str, topic: str, partition: int, offset: int
    ) -> FailedMessageDTO | None:
        pass
