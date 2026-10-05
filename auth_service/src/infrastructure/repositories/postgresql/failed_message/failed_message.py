from domain.failed_message.models import CreateFailedMessageDTO, FailedMessageDTO
from domain.failed_message.repository import AbstractFailedMessageRepository
from infrastructure.databases.postgresql.models.failed_message import FailedMessage as FailedMessageModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLFailedMessageRepository(AbstractFailedMessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateFailedMessageDTO) -> FailedMessageDTO:
        stmt = (
            insert(FailedMessageModel)
            .values(
                correlation_id=dto.correlation_id,
                event_id=dto.event_id,
                topic=dto.topic,
                attempts=dto.attempts,
                error_message=dto.error_message,
                error_type=dto.error_type,
                status=dto.status,
                consumer_name=dto.consumer_name,
                raw_key=dto.raw_key,
                raw_value=dto.raw_value,
                partition=dto.partition,
                offset=dto.offset,
                headers=dto.headers,
            )
            .on_conflict_do_nothing(constraint="unique_failed_kafka_message")
            .returning(FailedMessageModel)
        )
        result = await self._session.execute(stmt)
        failed_message = result.scalar_one_or_none()
        if failed_message is not None:
            return self._to_domain(failed_message)

        return await self.get_by_source(
            consumer_name=dto.consumer_name,
            topic=dto.topic,
            partition=dto.partition,
            offset=dto.offset,
        )

    async def get_by_source(
        self, consumer_name: str, topic: str, partition: int, offset: int
    ) -> FailedMessageDTO | None:
        stmt = select(FailedMessageModel).where(
            FailedMessageModel.consumer_name == consumer_name,
            FailedMessageModel.topic == topic,
            FailedMessageModel.partition == partition,
            FailedMessageModel.offset == offset,
        )

        result = await self._session.scalar(stmt)
        return self._to_domain(result) if result is not None else None

    async def delete(self, failed_message_id: int) -> None:
        pass

    async def get(self, failed_message_id: int) -> FailedMessageDTO | None:
        pass

    @staticmethod
    def _to_domain(failed_message: FailedMessageModel) -> FailedMessageDTO:
        return FailedMessageDTO(
            id=failed_message.id,
            correlation_id=failed_message.correlation_id,
            event_id=failed_message.event_id,
            topic=failed_message.topic,
            attempts=failed_message.attempts,
            error_message=failed_message.error_message,
            error_type=failed_message.error_type,
            status=failed_message.status,
            consumer_name=failed_message.consumer_name,
            raw_key=failed_message.raw_key,
            raw_value=failed_message.raw_value,
            partition=failed_message.partition,
            offset=failed_message.offset,
            headers=failed_message.headers,
            resolved_at=failed_message.resolved_at,
            failed_at=failed_message.failed_at,
        )
