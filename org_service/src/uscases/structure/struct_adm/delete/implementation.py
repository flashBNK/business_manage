import uuid

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.struct_adm.exceptions import InvalidRequestStructAdm, StructAdmHasUsers
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractDeleteStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLDeleteStructAdmUseCase(AbstractDeleteStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: uuid.UUID, company_id: uuid.UUID) -> None:
        correlation_id = uuid.uuid4()

        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm:
                return None
            if struct_adm.company_id != company_id:
                raise InvalidRequestStructAdm
            users_position = await uow.users_position.list_by_struct_adm(
                struct_adm_id=struct_adm_id, company_id=company_id, struct_adm_path=struct_adm.path
            )
            if users_position:
                raise StructAdmHasUsers

            await uow.struct_adm.delete(struct_adm_id=struct_adm_id)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.STRUCT_ADM_DELETED,
                    aggregate_id=struct_adm.id,
                    correlation_id=correlation_id,
                    payload={
                        "struct_adm_id": str(struct_adm.id),
                        "company_id": str(struct_adm.company_id),
                    },
                )
            )

            return None
