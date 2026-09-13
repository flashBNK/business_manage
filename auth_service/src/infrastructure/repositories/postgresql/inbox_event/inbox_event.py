from uuid import UUID

from domain.inbox_event.models import CreateInboxEventDTO, InboxEventDTO
from domain.inbox_event.repository import AbstractInboxEventRepository
from infrastructure.databases.postgresql.models.inbox_event import InboxEvent as InboxEventModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLInboxEventRepository(AbstractInboxEventRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateInboxEventDTO) -> InboxEventDTO:
        inbox_event = InboxEventModel(
            event_id=dto.event_id,
            consumer_name=dto.consumer_name,
        )

        self._session.add(inbox_event)
        await self._session.flush()

        return self._to_domain(inbox_event)

    async def delete(self, inbox_event_id: UUID) -> None:
        pass

    async def get_by_2_param(self, inbox_event_id: UUID, consumer_name: str) -> InboxEventDTO | None:
        stmt = select(InboxEventModel).where(
            InboxEventModel.event_id == inbox_event_id,
            InboxEventModel.consumer_name == consumer_name,
        )
        result = await self._session.execute(stmt)
        inbox_event = result.scalar_one_or_none()

        if not inbox_event:
            return None

        return self._to_domain(inbox_event)

    async def get(self, inbox_event_id: UUID) -> InboxEventDTO | None:
        stmt = select(InboxEventModel).where(InboxEventModel.event_id == inbox_event_id)
        result = await self._session.execute(stmt)
        inbox_event = result.scalar_one_or_none()

        if not inbox_event:
            return None

        return self._to_domain(inbox_event)

    @staticmethod
    def _to_domain(inbox_event: InboxEventModel) -> InboxEventDTO:
        return InboxEventDTO(
            event_id=inbox_event.event_id,
            consumer_name=inbox_event.consumer_name,
            processed_at=inbox_event.processed_at,
        )
