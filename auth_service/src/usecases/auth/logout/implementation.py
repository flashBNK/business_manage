from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from infrastructure.security.hash_token import hash_token

from .abstract import AbstractLogoutUseCase


class PostgreSQLLogoutUseCase(AbstractLogoutUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)

        async with self._uow as uow:
            stored = await uow.refresh_token.get_by_hash(token_hash=token_hash)
            if stored is not None:
                await uow.refresh_token.revoke(refresh_token_id=stored.id)
