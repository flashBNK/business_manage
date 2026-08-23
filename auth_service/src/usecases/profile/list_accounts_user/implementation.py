import uuid

from domain.account.models import AccountDTO
from domain.token.repository import AbstractTokenService
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from logger import get_logger

from .abstract import AbstractListAccountsUserUseCase

log = get_logger(__name__)


class PostgreSQLListAccountsUserUseCase(AbstractListAccountsUserUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, user_id: uuid.UUID) -> tuple[list[AccountDTO], int]:
        async with self._uow as uow:
            accounts, total = await uow.account.list_by_user_id(user_id=user_id)
            return accounts, total
