import datetime
import secrets

from domain.account.exceptions import EmailIsUsed
from domain.invite.models import CreateInviteDTO
from domain.member.models import (
    CreateEmployeeDTO,
    CreateEmployeeResultDTO,
    CreateMemberDTO,
)
from domain.user.models import CreateUserDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from logger import get_logger

from .abstract import AbstractCreateEmployeeUseCase

log = get_logger(__name__)


class PostgreSQLCreateEmployeeUseCase(AbstractCreateEmployeeUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateEmployeeDTO) -> CreateEmployeeResultDTO:
        async with self._uow as uow:
            account = await uow.account.get_by_email(dto.email)
            if account:
                raise EmailIsUsed(email=dto.email)

            user = await uow.user.create(CreateUserDTO(first_name=dto.first_name, last_name=dto.last_name))
            invite = CreateInviteDTO(
                email=dto.email,
                code=secrets.token_urlsafe(32),
                user_id=user.id,
                expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30),
            )
            invite = await uow.invite.create(invite)

            member = CreateMemberDTO(
                user_id=user.id,
                company_id=dto.company_id,
                role=dto.role,
                invite_id=invite.id,
            )
            member = await uow.member.create(member)

            log.info(
                "Ссылка приглашение создана",
                email=dto.email,
                company_id=str(dto.company_id),
                user_id=str(user.id),
                invite_code=invite.code,
            )

        return CreateEmployeeResultDTO(user_id=user.id, member_id=member.id)
