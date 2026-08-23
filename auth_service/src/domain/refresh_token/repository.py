from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import InvalidRefreshToken
from .models import CreateRefreshTokenDTO, RefreshTokenDTO


class AbstractRefreshTokenRepository(AbstractRepository[RefreshTokenDTO, UUID, CreateRefreshTokenDTO], ABC):
    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> RefreshTokenDTO | None:
        raise InvalidRefreshToken

    @abstractmethod
    async def revoke(self, refresh_token_id: UUID) -> None:
        raise InvalidRefreshToken

    @abstractmethod
    async def revoke_all_by_user_id(self, user_id: UUID) -> None:
        raise InvalidRefreshToken
