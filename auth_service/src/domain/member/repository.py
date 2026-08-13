from abc import ABC, abstractmethod

from .exceptions import MembersNotFound
from domain.abstract import AbstractRepository
from .models import MemberDTO, CreateMemberDTO


class AbstractMemberRepository(AbstractRepository[MemberDTO, int, CreateMemberDTO], ABC):
    @abstractmethod
    def get_by_user_id(self, user_id) -> list[MemberDTO] | None:
        raise MembersNotFound

    # @abstractmethod
    # async def update(self, id: int, dto: UpdateDTO) -> DTO:
    #     raise MembersNotFound