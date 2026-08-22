from datetime import datetime, UTC

from domain.refresh_token.exceptions import InvalidRefreshToken
from domain.refresh_token.issue_tokens import issue_token_pair
from domain.token.models import TokenDTO, MembershipAdmission, LoginResultDTO
from domain.token.repository import AbstractTokenService
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from infrastructure.security.hash_token import hash_token
from .abstract import AbstractRefreshUseCase
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLRefreshUseCase(AbstractRefreshUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, refresh_token: str) -> LoginResultDTO:
        token_hash = hash_token(refresh_token)

        async with self._uow as uow:
            stored = await uow.refresh_token.get_by_hash(token_hash=token_hash)

            if stored is None or stored.expires_at < datetime.now(UTC):
                raise InvalidRefreshToken

            if stored.revoked_at is not None:
                log.warning("Revoked refresh token reuse detected.", user_id=str(stored.user_id))
                await uow.refresh_token.revoke_all_by_user_id(user_id=stored.user_id)
                await uow.commit()
                raise InvalidRefreshToken

            await uow.refresh_token.revoke(refresh_token_id=stored.id)

            members = await uow.member.get_by_user_id(user_id=stored.user_id)
            payload = TokenDTO(
                subject=stored.user_id,
                memberships=[MembershipAdmission(company_id=m.company_id, role=m.role) for m in members],
            )

            result = await issue_token_pair(uow=uow, token_service=self._token_service, payload=payload)

        return result