import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import TicketNotFound
from .models import CreateTicketDTO, TicketDTO


class AbstractTicketRepository(AbstractRepository[TicketDTO, uuid.UUID, CreateTicketDTO], ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> TicketDTO | None:
        raise TicketNotFound

    @abstractmethod
    async def update(self, ticket_id: UUID) -> TicketDTO:
        raise TicketNotFound
