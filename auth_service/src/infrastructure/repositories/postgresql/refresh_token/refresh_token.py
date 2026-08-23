import datetime
import uuid

from domain.refresh_token.models import CreateRefreshTokenDTO, RefreshTokenDTO
from domain.refresh_token.repository import AbstractRefreshTokenRepository
from infrastructure.databases.postgresql.models.refresh_token import (
    RefreshToken as RefreshTokenModel,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLRefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateRefreshTokenDTO) -> RefreshTokenDTO:
        db_refresh_token = RefreshTokenModel(
            user_id=dto.user_id,
            token_hash=dto.token_hash,
            expires_at=dto.expires_at,
        )

        self._session.add(db_refresh_token)
        await self._session.flush()

        return self._to_domain(db_refresh_token)

    async def revoke(self, refresh_token_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == refresh_token_id)
            .values(revoked_at=datetime.datetime.now(datetime.UTC))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def revoke_all_by_user_id(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.datetime.now(datetime.UTC))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete(self, refresh_token_id: uuid.UUID) -> None:
        pass

    async def get(self, refresh_token_id: uuid.UUID) -> RefreshTokenDTO:
        pass

    async def get_by_hash(self, token_hash: str) -> RefreshTokenDTO | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        result = await self._session.execute(stmt)
        refresh_token = result.scalar_one_or_none()

        if refresh_token is None:
            return None

        return self._to_domain(refresh_token)

    @staticmethod
    def _to_domain(secret: RefreshTokenModel) -> RefreshTokenDTO:
        return RefreshTokenDTO(
            id=secret.id,
            user_id=secret.user_id,
            expires_at=secret.expires_at,
            revoked_at=secret.revoked_at,
        )
