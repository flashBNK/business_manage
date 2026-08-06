import datetime

from domain.account.models import ConfirmAccountDTO, AccountDTO, CreateAccountDTO
from domain.invite.exceptions import InvalidOrExpiredCode, TooManyAttempts
from domain.invite.models import UpdateInviteDTO
from infrastructure.databases.postgresql.models.invite import InviteStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from .abstract import AbstractConfirmAccountUseCase
from logger import get_logger

log = get_logger(__name__)

MAX_ATTEMPTS = 5

class PostgreSQLConfirmAccountUseCase(AbstractConfirmAccountUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, dto: ConfirmAccountDTO) -> AccountDTO:

        async with self._uow as uow:
            invite = await uow.invite.get_by_email(dto.email)
            log.info("Проверка", invite=invite)
            if not invite or invite.expires_at < datetime.datetime.now(datetime.UTC):
                raise InvalidOrExpiredCode
            if invite.attempts >= MAX_ATTEMPTS:
                raise TooManyAttempts
            if invite.code != dto.code:
                invite.attempts += 1
                await uow.invite.update(UpdateInviteDTO(attempts=invite.attempts, email=invite.email))
                log.warning("Неверный код подтверждения", email=dto.email, attempts=invite.attempts)
                raise InvalidOrExpiredCode

            log.info("Проверка кода", code_invite=invite.code, new_code=dto.code)

            invite.status = InviteStatus.ACCEPTED
            invite.accepted_at = datetime.datetime.now(datetime.UTC)
            await uow.invite.update(dto=invite, invite_id=invite.id)
            account = await uow.account.create(dto=CreateAccountDTO(email=invite.email))

            log.info("Аккаунт подтверждён через код по email", email=dto.email, code=dto.code)

            return account