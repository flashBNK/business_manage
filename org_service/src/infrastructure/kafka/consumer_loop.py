from json import loads

from domain.inbox_event.models import CreateInboxEventDTO
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.di.injection import build_unit_of_work
from infrastructure.kafka.consumer import KafkaEventConsumer
from infrastructure.kafka.hendlers import EVENT_HANDLERS
from logger import get_logger

log = get_logger(__name__)

CONSUMER_NAME = "org_service"


async def run_event_consumer(consumer: KafkaEventConsumer, session_manager: DatabaseSessionManager) -> None:
    try:
        async for message in consumer:
            event = EventEnvelopeDTO.from_dict(loads(message.value.decode()))
            event_id = event.event_id

            async with session_manager.session() as session:
                async with build_unit_of_work(session=session) as uow:
                    already_processed = await uow.inbox_event.get_by_2_param(
                        inbox_event_id=event_id, consumer_name=CONSUMER_NAME
                    )

                    if already_processed is not None:
                        await consumer.commit()
                        continue

                    handler = EVENT_HANDLERS.get(event.event_type)
                    if handler is None:
                        log.warning("Нет обработчика для типа события", event_type=event.event_type)
                    else:
                        await handler(event=event, uow=uow)

                    await uow.inbox_event.create(CreateInboxEventDTO(consumer_name=CONSUMER_NAME, event_id=event_id))

            await consumer.commit()
    except Exception as exc:
        log.exception("kafka consumer crashed", exception=exc)

    finally:
        await consumer.stop()
