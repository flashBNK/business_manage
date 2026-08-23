import uuid

from domain.outbox_event.dedup_key import compute_dedup_key
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventDTO, OutboxEventType
from domain.outbox_event.repository import AbstractOutboxEventRepository
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent as OutboxEventModel
from sqlalchemy.ext.asyncio import AsyncSession

SERVICE_NAME = "auth_service"


class PostgreSQLOutboxEventRepository(AbstractOutboxEventRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateOutboxEventDTO) -> OutboxEventDTO:
        dedup_key = compute_dedup_key(event_type=dto.event_type, aggregate_id=dto.aggregate_id, payload=dto.payload)

        db_outbox_event = OutboxEventModel(
            event_type=dto.event_type.value,
            payload=dto.payload,
            aggregate_id=dto.aggregate_id,
            schema_version=dto.schema_version,
            correlation_id=dto.correlation_id or uuid.uuid4(),
            causation_id=dto.causation_id,
            dedup_key=dedup_key,
            producer=SERVICE_NAME,
        )

        self._session.add(db_outbox_event)
        await self._session.flush()

        return self._to_domain(db_outbox_event)

    async def delete(self, outbox_event_id: int) -> None:
        pass

    async def get(self, outbox_event_id: int) -> OutboxEventDTO | None:
        pass

    @staticmethod
    def _to_domain(outbox_event: OutboxEventModel) -> OutboxEventDTO:
        return OutboxEventDTO(
            event_id=outbox_event.event_id,
            event_type=OutboxEventType(outbox_event.event_type),
            aggregate_id=outbox_event.aggregate_id,
            correlation_id=outbox_event.correlation_id,
            causation_id=outbox_event.causation_id,
            payload=outbox_event.payload,
            schema_version=outbox_event.schema_version,
            dedup_key=outbox_event.dedup_key,
            producer=outbox_event.producer,
            occurred_at=outbox_event.occurred_at,
            published_at=outbox_event.published_at,
        )
