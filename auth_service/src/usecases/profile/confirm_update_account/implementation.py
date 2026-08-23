import datetime

from domain.account.exceptions import AccountForbidden
from domain.account.models import AccountDTO, ConfirmEmailChangeDTO, UpdateAccountDTO
from domain.invite.exceptions import InvalidOrExpiredCode
from infrastructure.databases.postgresql.models.invite import InviteStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from logger import get_logger

from .abstract import AbstractConfirmUpdateAccountUseCase

log = get_logger(__name__)


class PostgreSQLConfirmUpdateAccountUseCase(AbstractConfirmUpdateAccountUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, dto: ConfirmEmailChangeDTO) -> AccountDTO:
        async with self._uow as uow:
            invite = await uow.invite.get_by_code(dto.invite_code)
            log.info("Проверка", invite=invite)

            if not invite or invite.status != InviteStatus.PENDING:
                raise InvalidOrExpiredCode

            if invite.expires_at is not None and invite.expires_at < datetime.datetime.now(datetime.UTC):
                raise InvalidOrExpiredCode

            if invite.user_id != dto.user_id or invite.account_id != dto.account_id:
                raise AccountForbidden

            invite.status = InviteStatus.ACCEPTED
            invite.accepted_at = datetime.datetime.now(datetime.UTC)
            await uow.invite.update(dto=invite, invite_id=invite.id)

            account = await uow.account.update(dto=UpdateAccountDTO(email=invite.email), account_id=dto.account_id)
            return account
