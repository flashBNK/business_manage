import datetime
import uuid

from domain.account.exceptions import AccountForbidden
from domain.account.models import AccountDTO, ConfirmEmailChangeDTO, UpdateAccountDTO
from domain.invite.exceptions import InvalidOrExpiredCode
from domain.invite.models import UpdateInviteDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from infrastructure.databases.postgresql.models.invite import InviteStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from logger import get_logger

from .abstract import AbstractConfirmUpdateAccountUseCase

log = get_logger(__name__)


class PostgreSQLConfirmUpdateAccountUseCase(AbstractConfirmUpdateAccountUseCase):
    def __init__(self, uow: PostgreSQLAuthUnitOfWork):
        self._uow = uow

    async def execute(self, dto: ConfirmEmailChangeDTO) -> AccountDTO:
        correlation_id = uuid.uuid4()

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
            await uow.invite.update(
                dto=UpdateInviteDTO(status=invite.status, accepted_at=invite.accepted_at), invite_id=invite.id
            )

            old_email = (await uow.account.get(account_id=dto.account_id)).email
            account = await uow.account.update(dto=UpdateAccountDTO(email=invite.email), account_id=dto.account_id)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_EMAIL_CHANGED,
                    aggregate_id=invite.user_id,
                    correlation_id=correlation_id,
                    payload={"user_id": str(invite.user_id), "old_email": old_email, "new_email": account.email},
                )
            )

            return account
