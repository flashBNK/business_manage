from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import InboxEventNotFound
from .models import CreateInboxEventDTO, InboxEventDTO


class AbstractInboxEventRepository(AbstractRepository[InboxEventDTO, UUID, CreateInboxEventDTO], ABC):
    @abstractmethod
    async def get_by_2_param(self, inbox_event_id: UUID, consumer_name: str) -> InboxEventDTO | None:
        raise InboxEventNotFound

    # @abstractmethod
    # async def upsert(self, dto: CreateInboxEventDTO) -> InboxEventDTO:
    #     raise InboxEventNotFound
