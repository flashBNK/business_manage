import datetime
import secrets
import uuid

from domain.account.exceptions import AccountForbidden, EmailIsUsed, AccountNotFound
from domain.account.models import RequestEmailChangeDTO
from domain.invite.models import CreateInviteDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from .abstract import AbstractUpdateAccountUseCase
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLUpdateAccountUseCase(AbstractUpdateAccountUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, dto: RequestEmailChangeDTO, account_id: uuid.UUID) -> None:
        async with self._uow as uow:
            current_account = await uow.account.get(account_id)
            if not current_account:
                raise AccountNotFound

            accounts, total = await uow.account.list_by_user_id(user_id=dto.user_id)
            if account_id not in [account.id for account in accounts]:
                raise AccountForbidden
            if await uow.account.get_by_email(dto.new_email):
                raise EmailIsUsed(email=dto.new_email)

            code = f"{secrets.randbelow(1_000_000):06d}"

            dto_invite = CreateInviteDTO(
                email=dto.new_email,
                code=code,
                user_id=dto.user_id,
                account_id=account_id,
                expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15),
            )
            await uow.invite.create(dto_invite)

            log.info("Код подтверждения сгенерирован", new_email=dto.new_email, code=code)