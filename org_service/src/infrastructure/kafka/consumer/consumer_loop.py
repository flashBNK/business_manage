import asyncio
from json import loads, JSONDecodeError

from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.di.injection import build_unit_of_work
from infrastructure.kafka.consumer.consumer import KafkaEventConsumer
from infrastructure.kafka.consumer.handlers import EVENT_HANDLERS
from infrastructure.kafka.consumer.retry import process_event_with_retry
from logger import get_logger

log = get_logger(__name__)

CONSUMER_NAME = "org_service"


async def run_event_consumer(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager) -> None:
    try:
        async for message in consumer:
            try:
                await process_message(consumer=consumer, session_manager=session_manager, message=message)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Error processing Kafka message",
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                )
    except asyncio.CancelledError:
        raise
    finally:
        await consumer.stop()


async def process_message(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager, message) -> None:
    try:
        event_dict = loads(message.value.decode())
        event = EventEnvelopeDTO.from_dict(event_dict)

    except (UnicodeDecodeError, JSONDecodeError, KeyError, TypeError, ValueError):
        log.exception("Failed to parse Kafka event",
            topic=message.topic,
            partition=message.partition,
            offset=message.offset,
        )
        await consumer.commit_message(message=message)
        return

    async with session_manager.session() as session:
        async with build_unit_of_work(session=session) as uow:
            already_processed = await uow.inbox_event.get_by_2_param(
                inbox_event_id=event.event_id,
                consumer_name=CONSUMER_NAME
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
        await consumer.commit_message(message=message)
        return

    success = await process_event_with_retry(
        event=event,
        handler=handler,
        session_manager=session_manager,
        consumer_name=CONSUMER_NAME
    )

    if success:
        await consumer.commit_message(message)
        return

    log.error(
        "Kafka event failed after all retry attempts",
        event_id=event.event_id,
        event_type=event.event_type,
    )

    await consumer.commit_message(message)
