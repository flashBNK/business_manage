from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.position.models import PositionDTO, UpdatePositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractUpdatePositionUseCase


class PostgreSQLUpdatePositionUseCase(AbstractUpdatePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: UpdatePositionDTO, company_id: UUID, position_id: UUID) -> PositionDTO:
        correlation_id = uuid4()
        async with self._uow as uow:
            position = await uow.position.get(position_id=position_id)

            if not position or position.company_id != company_id:
                raise PositionNotFound

            position = await uow.position.update(dto=dto, position_id=position_id)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.POSITION_UPDATED,
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

            return position
