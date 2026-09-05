import uuid

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.models import CreatePositionDTO, PositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractCreatePositionUseCase


class PostgreSQLCreatePositionUseCase(AbstractCreatePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreatePositionDTO) -> PositionDTO:
        correlation_id = uuid.uuid4()
        async with self._uow as uow:
            position = await uow.position.create(dto=dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.POSITION_CREATED,
                    aggregate_id=position.id,
                    correlation_id=correlation_id,
                    payload={
                        "company_id": str(dto.company_id),
                        "position_id": str(position.id),
                        "name": str(position.name),
                        "description": str(position.description),
                    },
                )
            )

            return position
