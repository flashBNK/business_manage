import secrets
from datetime import UTC, datetime, timedelta

from domain.refresh_token.models import CreateRefreshTokenDTO
from domain.token.models import LoginResultDTO, TokenDTO
from domain.token.repository import AbstractTokenService
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from infrastructure.security.hash_token import hash_token

REFRESH_TOKEN_TTL = timedelta(days=14)


async def issue_token_pair(
    uow: PostgreSQLAuthUnitOfWork, token_service: AbstractTokenService, payload: TokenDTO
) -> LoginResultDTO:
    access_token = token_service.create_access_token(payload=payload)

    refresh_token = secrets.token_urlsafe(64)
    dto_token = CreateRefreshTokenDTO(
        user_id=payload.subject,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(UTC) + REFRESH_TOKEN_TTL,
    )
    await uow.refresh_token.create(dto=dto_token)

    return LoginResultDTO(access_token=access_token, refresh_token=refresh_token)
