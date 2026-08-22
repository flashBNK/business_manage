import datetime

from domain.account.models import CreateAccountDTO
from domain.invite.exceptions import InviteAlreadyUsed, InvalidOrExpiredCode
from domain.invite.models import UpdateInviteDTO, CompleteEmployeeInviteDTO
from domain.refresh_token.issue_tokens import issue_token_pair
from domain.secret.models import CreateSecretDTO
from domain.token.models import TokenDTO, MembershipAdmission, LoginResultDTO
from domain.token.repository import AbstractTokenService
from infrastructure.databases.postgresql.models.invite import InviteStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from .abstract import AbstractCompleteEmployeeInviteUseCase
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLCompleteEmployeeInviteUseCase(AbstractCompleteEmployeeInviteUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, dto: CompleteEmployeeInviteDTO) -> LoginResultDTO:
        async with self._uow as uow:
            invite = await uow.invite.get_by_code(code=dto.invite_token)
            if not invite:
                raise InvalidOrExpiredCode
            elif invite.expires_at < datetime.datetime.now(datetime.UTC):
                raise InvalidOrExpiredCode
            elif invite.status != InviteStatus.PENDING:
                raise InviteAlreadyUsed

            account = await uow.account.create(
                CreateAccountDTO(email=invite.email)
            )

            await uow.secret.create(
                CreateSecretDTO(
                    password=dto.password,
                    user_id=invite.user_id,
                    account_id=account.id
                )
            )

            member = await uow.member.get_by_invite_id(invite_id=invite.id)
            member = await uow.member.activation_shift(member_id=member.id, flag=True)

            invite = await uow.invite.update(
                invite_id=invite.id,
                dto=UpdateInviteDTO(status=InviteStatus.ACCEPTED)
            )

            log.info(
                "Регистрация сотрудника завершена",
                user_id=str(invite.user_id),
                company_id=str(member.company_id),
            )

            payload = TokenDTO(
                subject=invite.user_id,
                memberships=[MembershipAdmission(company_id=member.company_id, role=member.role)],
            )

            return await issue_token_pair(uow=uow, payload=payload, token_service=self._token_service)