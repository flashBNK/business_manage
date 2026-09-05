from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.struct_adm_position.exceptions import StructAdmPositionIsUsed
from domain.users_position.exceptions import UsersPositionIsUsed
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractDeletePositionUseCase


class PostgreSQLDeletePositionUseCase(AbstractDeletePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, position_id: UUID) -> None:
        correlation_id = uuid4()
        async with self._uow as uow:
            struct_adm_position = await uow.struct_adm_position.list_by_position_id(position_id=position_id)
            if struct_adm_position:
                raise StructAdmPositionIsUsed

            users_position = await uow.users_position.list_by_position(position_id=position_id, company_id=company_id)
            if users_position:
                raise UsersPositionIsUsed

            position = await uow.position.get(position_id=position_id)
            if not position or position.company_id != company_id:
                raise PositionNotFound

            await uow.position.delete(position_id=position_id)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.POSITION_DELETED,
                    aggregate_id=position.id,
                    correlation_id=correlation_id,
                    payload={
                        "company_id": str(company_id),
                        "position_id": str(position.id),
                        "name": str(position.name),
                        "description": str(position.description),
                    },
                )
            )