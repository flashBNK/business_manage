import datetime
import secrets

from domain.account.exceptions import EmailIsUsed
from domain.account.models import CreateAccountDTO
from domain.invite.models import CreateInviteDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from logger import get_logger

from .abstract import AbstractCheckAccountUseCase

log = get_logger(__name__)


class PostgreSQLCheckAccountUseCase(AbstractCheckAccountUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateAccountDTO) -> None:

        async with self._uow as uow:
            account = await uow.account.get_by_email(dto.email)
            if account:
                raise EmailIsUsed(email=dto.email)

            code = f"{secrets.randbelow(1_000_000):06d}"
            dto_invite = CreateInviteDTO(
                email=dto.email,
                code=code,
                expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15),
            )

            await uow.invite.create(dto=dto_invite)

            log.info("Код подтверждения сгенерирован", email=dto.email, code=code)
