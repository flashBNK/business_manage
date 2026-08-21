from abc import ABC, abstractmethod

from .exceptions import InviteNotFound
from domain.abstract import AbstractRepository
from .models import InviteDTO, CreateInviteDTO, UpdateInviteDTO


class AbstractInviteRepository(ABC):
    @abstractmethod
    async def update(self, invite_id: int, dto: UpdateInviteDTO) -> InviteDTO:
        raise InviteNotFound

    @abstractmethod
    async def get_by_code(self, code: str) -> InviteDTO | None:
        raise InviteNotFound