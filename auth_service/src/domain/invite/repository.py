import uuid
from abc import ABC, abstractmethod

from .exceptions import InviteNotFound
from .models import InviteDTO, UpdateInviteDTO


class AbstractInviteRepository(ABC):
    @abstractmethod
    async def update(self, invite_id: int, dto: UpdateInviteDTO) -> InviteDTO:
        raise InviteNotFound

    @abstractmethod
    async def get_by_code(self, code: str) -> InviteDTO | None:
        raise InviteNotFound

    @abstractmethod
    async def get_by_account_id(self, account_id: uuid.UUID) -> InviteDTO | None:
        raise InviteNotFound
