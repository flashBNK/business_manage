import uuid

from domain.account.exceptions import AccountAlreadyRegistered, EmailNotFound
from domain.account.models import CompleteSignUpDTO
from domain.company.exceptions import CompanyNameIsUsed
from domain.company.models import CreateCompanyDTO
from domain.member.models import CreateMemberDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.refresh_token.issue_tokens import issue_token_pair
from domain.secret.models import CreateSecretDTO
from domain.token.models import LoginResultDTO, MembershipAdmission, TokenDTO
from domain.token.repository import AbstractTokenService
from domain.user.models import CreateUserDTO
from infrastructure.databases.postgresql.models.members import MemberRoles
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from logger import get_logger

from .abstract import AbstractCompleteSignUpUseCase

log = get_logger(__name__)


class PostgreSQLCompleteSignUpUseCase(AbstractCompleteSignUpUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, dto: CompleteSignUpDTO) -> LoginResultDTO:
        correlation_id = uuid.uuid4()
        company = None
        member = None

        async with self._uow as uow:
            account = await uow.account.get_by_email(dto.email)
            if account is None:
                raise EmailNotFound

            if await uow.secret.get_by_account_id(account.id):
                raise AccountAlreadyRegistered

            user = await uow.user.create(CreateUserDTO(first_name=dto.first_name, last_name=dto.last_name))
            await uow.secret.create(CreateSecretDTO(account_id=account.id, user_id=user.id, password=dto.password))

            if dto.company_name:
                if await uow.company.get_by_name(company_dto=CreateCompanyDTO(name=dto.company_name)) is None:
                    company = await uow.company.create(CreateCompanyDTO(name=dto.company_name))
                    member = await uow.member.create(
                        CreateMemberDTO(
                            user_id=user.id,
                            company_id=company.id,
                            role=MemberRoles.OWNER,
                            is_active=True,
                        )
                    )
                else:
                    raise CompanyNameIsUsed

            if company:
                await uow.outbox_event.create(
                    CreateOutboxEventDTO(
                        event_type=OutboxEventType.COMPANY_CREATED,
                        aggregate_id=company.id,
                        correlation_id=correlation_id,
                        payload={
                            "company_id": str(company.id),
                            "name": company.name,
                        },
                    )
                )

                await uow.outbox_event.create(
                    CreateOutboxEventDTO(
                        event_type=OutboxEventType.EMPLOYEE_CREATED,
                        aggregate_id=user.id,
                        correlation_id=correlation_id,
                        payload={
                            "user_id": str(user.id),
                            "company_id": str(member.company_id),
                            "first_name": dto.first_name,
                            "last_name": dto.last_name,
                            "email": dto.email,
                            "role": member.role.value,
                            "is_active": member.is_active,
                        },
                    )
                )

                log.info(
                    "Компания и администратор созданы",
                    company_id=str(company.id),
                    user_id=str(user.id),
                )

                payload = TokenDTO(
                    subject=user.id,
                    memberships=[MembershipAdmission(company_id=member.company_id, role=member.role)],
                )
            else:
                log.info(
                    "Пользователь создан",
                    user_id=str(user.id),
                )

                payload = TokenDTO(
                    subject=user.id,
                    memberships=[],
                )

            return await issue_token_pair(uow=uow, payload=payload, token_service=self._token_service)
