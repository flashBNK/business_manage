import asyncio
from base64 import b64encode
from json import JSONDecodeError, loads

from aiokafka import TopicPartition
from aiokafka.errors import KafkaConnectionError, KafkaTimeoutError
from domain.failed_message.models import CreateFailedMessageDTO
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.failed_message import FailedMessageStatus
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.di.injection import build_unit_of_work
from infrastructure.kafka.consumer.consumer import KafkaEventConsumer
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.kafka.consumer.retry import process_event_with_retry
from logger import get_logger
from sqlalchemy.exc import OperationalError

log = get_logger(__name__)

CONSUMER_NAME = "auth_service"


async def save_failed_message(
    session_manager: DatabaseSessionManager,
    message,
    error_type,
    error_message,
    attempts,
    event: EventEnvelopeDTO | None = None,
) -> None:
    async with session_manager.session() as session:
        async with build_unit_of_work(session=session) as uow:
            dto = CreateFailedMessageDTO(
                consumer_name=CONSUMER_NAME,
                topic=message.topic,
                partition=message.partition,
                offset=message.offset,
                raw_value=message.value,
                headers=[
                    {
                        "key": key,
                        "value_base64": b64encode(value).decode("ascii") if value is not None else None,
                    }
                    for key, value in (message.headers or [])
                ],
                error_type=error_type,
                error_message=error_message,
                attempts=attempts,
                status=FailedMessageStatus.PENDING,
                raw_key=message.key,
                event_id=event.event_id if event is not None else None,
                correlation_id=event.correlation_id if event is not None else None,
            )
            await uow.failed_message.create(dto=dto)


async def run_event_consumer(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager) -> None:
    try:
        async for message in consumer:
            try:
                await process_message(consumer=consumer, session_manager=session_manager, message=message)
            except asyncio.CancelledError:
                raise
            except (OSError, OperationalError, KafkaConnectionError, KafkaTimeoutError):
                log.exception(
                    "Error processing Kafka message",
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )

                topic_partition = TopicPartition(message.topic, message.partition)

                consumer.pause(topic_partition)
                consumer.seek(topic_partition, message.offset)

                await asyncio.sleep(1)

                consumer.resume(topic_partition)

            except:
                log.exception(
                    "Error processing Kafka message",
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )
                raise

    except asyncio.CancelledError:
        raise
    finally:
        await consumer.stop()


async def process_message(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager, message) -> None:
    try:
        async with session_manager.session() as session:
            async with build_unit_of_work(session=session) as uow:
                saved_failure = await uow.failed_message.get_by_source(
                    consumer_name=CONSUMER_NAME,
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )

        if saved_failure is not None:
            return await consumer.commit_message(message)

        if message.value is None:
            raise ValueError("Kafka message value is None")

        event_dict = loads(message.value.decode("utf-8"))

        if not isinstance(event_dict, dict):
            raise ValueError("Kafka event envelope must be a JSON object")

        event = EventEnvelopeDTO.from_dict(event_dict)

    except (UnicodeDecodeError, JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        log.exception(
            "Failed to parse Kafka event",
            topic=message.topic,
            partition=message.partition,
            offset=message.offset,
        )
        await save_failed_message(
            session_manager=session_manager,
            message=message,
            error_type=type(exc).__name__,
            error_message=str(exc),
            attempts=0,
        )
        return await consumer.commit_message(message)

    async with session_manager.session() as session:
        async with build_unit_of_work(session=session) as uow:
            already_processed = await uow.inbox_event.get_by_2_param(
                inbox_event_id=event.event_id, consumer_name=CONSUMER_NAME
            )
            if already_processed is not None:
                log.info("Kafka event already processed", event_id=event.event_id, event_type=event.event_type)
                await consumer.commit_message(message=message)
                return

    handler = EVENT_HANDLERS.get(event.event_type)

    if not handler:
        log.warning(
            "No handler for Kafka event",
            event_id=event.event_id,
            event_type=event.event_type,
        )
        return await consumer.commit_message(message=message)

    result = await process_event_with_retry(
        event=event, handler=handler, session_manager=session_manager, consumer_name=CONSUMER_NAME
    )

    if result.success:
        return await consumer.commit_message(message)

    log.error(
        "Kafka event failed after all retry attempts",
        event_id=event.event_id,
        event_type=event.event_type,
    )

    await save_failed_message(
        session_manager=session_manager,
        message=message,
        error_type=result.error_type,
        error_message=result.error_message,
        attempts=result.attempts,
        event=event,
    )

    return await consumer.commit_message(message)
