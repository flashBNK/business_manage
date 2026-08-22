from domain.refresh_token.issue_tokens import issue_token_pair
from domain.token.models import LoginDTO, TokenDTO, MembershipAdmission, LoginResultDTO
from domain.account.exceptions import EmailNotFound
from domain.token.repository import AbstractTokenService
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from .abstract import AbstractLoginUseCase
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLLoginUseCase(AbstractLoginUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, dto: LoginDTO) -> LoginResultDTO:

        async with self._uow as uow:
            account = await uow.account.get_by_email(dto.email)
            if account is None:
                raise EmailNotFound

            secret = await uow.secret.check_and_get_by_account_id(account_id=account.id, password=dto.password)

            members = await uow.member.get_by_user_id(user_id=secret.user_id)

            payload = TokenDTO(
                subject=secret.user_id,
                memberships=[
                    MembershipAdmission(
                        company_id=member.company_id,
                        role=member.role,
                    )
                    for member in members
                ]
            )

            return await issue_token_pair(uow=uow, payload=payload, token_service=self._token_service)
