import uuid

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import CreateStructAdmDTO, StructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractCreateStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLCreateStructAdmUseCase(AbstractCreateStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateStructAdmDTO, parent_id: uuid.UUID) -> StructAdmDTO:
        correlation_id = uuid.uuid4()

        async with self._uow as uow:
            parent = await uow.struct_adm.get(struct_adm_id=parent_id)
            if not parent or parent.company_id != dto.company_id:
                raise InvalidRequestStructAdm

            path = f"{parent.path}.n{dto.id.hex}"
            dto.path = path

            struct_adm_dto = CreateStructAdmDTO(
                id=dto.id,
                company_id=parent.company_id,
                name=dto.name,
                path=path,
            )

            struct_adm = await uow.struct_adm.create(dto=struct_adm_dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.STRUCT_ADM_CREATED,
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
