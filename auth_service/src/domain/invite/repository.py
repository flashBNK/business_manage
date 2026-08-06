from abc import ABC, abstractmethod

from .exceptions import InviteNotFound
from domain.abstract import AbstractRepository
from .models import InviteDTO, CreateInviteDTO, UpdateInviteDTO


class AbstractInviteRepository(AbstractRepository[InviteDTO, int, CreateInviteDTO], ABC):
    @abstractmethod
    async def update(self, invite_id: int, dto: UpdateInviteDTO) -> InviteDTO:
        raise InviteNotFound