import uuid

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import StructAdmDTO, UpdateStructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractRenameStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLRenameStructAdmUseCase(AbstractRenameStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: uuid.UUID, company_id: uuid.UUID, dto: UpdateStructAdmDTO) -> StructAdmDTO:
        correlation_id = uuid.uuid4()
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm:
                raise InvalidRequestStructAdm
            if struct_adm.company_id != company_id:
                raise InvalidRequestStructAdm

            struct_adm = await uow.struct_adm.update(struct_adm_id=struct_adm_id, dto=dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.STRUCT_ADM_UPDATED,
                    aggregate_id=struct_adm.id,
                    correlation_id=correlation_id,
                    payload={
                        "struct_adm_id": str(struct_adm.id),
                        "company_id": str(struct_adm.company_id),
                        "name": struct_adm.name,
                        "path": struct_adm.path,
                    },
                )
            )

            return struct_adm
