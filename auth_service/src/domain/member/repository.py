import uuid
from abc import ABC, abstractmethod

from domain.abstract import AbstractRepository

from .exceptions import MembersNotFound
from .models import CreateMemberDTO, MemberDTO


class AbstractMemberRepository(AbstractRepository[MemberDTO, int, CreateMemberDTO], ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: uuid.UUID) -> list[MemberDTO] | None:
        raise MembersNotFound

    @abstractmethod
    def activation_shift(self, member_id: uuid.UUID, flag: bool) -> MemberDTO | None:
        raise MembersNotFound

    @abstractmethod
    async def get_by_invite_id(self, invite_id: uuid.UUID) -> MemberDTO | None:
        raise MembersNotFound

    # @abstractmethod
    # async def update(self, id: int, dto: UpdateDTO) -> DTO:
    #     raise MembersNotFound
