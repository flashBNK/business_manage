import secrets
import datetime

from domain.account.models import CreateAccountDTO, AccountDTO

from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from .abstract import AbstractCheckAccountUseCase
from domain.account.exceptions import EmailIsUsed
from domain.invite.models import CreateInviteDTO
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLCheckAccountUseCase(AbstractCheckAccountUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateAccountDTO) -> None:

        async with self._uow as uow:
            if await uow.account.get_by_email(dto.email):
                raise EmailIsUsed(email=dto.email)

            code = f"{secrets.randbelow(1_000_000):06d}"
            dto_invite = CreateInviteDTO(
                email=dto.email,
                code=code,
                expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)
            )

            await uow.invite.create(dto=dto_invite)

            log.info("Код подтверждения сгенерирован", email=dto.email, code=code)

