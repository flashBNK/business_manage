from json import loads

from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.inbox_event import InboxEvent
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.consumer import KafkaEventConsumer
from infrastructure.kafka.hendlers import EVENT_HANDLERS
from logger import get_logger

log = get_logger(__name__)


async def run_event_consumer(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager) -> None:
    try:
        async for message in consumer:
            event = EventEnvelopeDTO.from_dict(loads(message.value.decode()))
            event_id = event.event_id

            async with session_manager.session() as session:
                already_processed = await session.get(
                    InboxEvent, {"consumer_name": "org_service", "event_id": event_id}
                )

                if already_processed is not None:
                    await consumer.commit()
                    continue

                handler = EVENT_HANDLERS.get(event.event_type)
                if handler is None:
                    log.warning("Нет обработчика для типа события", event_type=event.event_type)
                else:
                    await handler(event=event, session=session)

                session.add(InboxEvent(consumer_name="org_service", event_id=event_id))
                await session.commit()

            await consumer.commit()
    except Exception as exc:
        log.exception("kafka consumer crashed", exception=exc)

    finally:
        await consumer.stop()
