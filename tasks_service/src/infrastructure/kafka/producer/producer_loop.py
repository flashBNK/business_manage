import asyncio

from domain.outbox_event.models import OutboxEventType
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.producer.producer import KafkaEventProducer
from infrastructure.repositories.postgresql.outbox_event import PostgreSQLOutboxEventRepository
from logger import get_logger

log = get_logger(__name__)

TOPIC_EVENT_TYPE = {
    OutboxEventType.STRUCT_ADM_CREATED: "org.struct_adm.events",
    OutboxEventType.STRUCT_ADM_UPDATED: "org.struct_adm.events",
    OutboxEventType.STRUCT_ADM_DELETED: "org.struct_adm.events",
    OutboxEventType.EMPLOYEE_POSITION_CHANGED: "org.employee.events",
    OutboxEventType.EMPLOYEE_POSITION_DELETED: "org.employee.events",
    OutboxEventType.POSITION_CREATED: "org.position.events",
    OutboxEventType.POSITION_UPDATED: "org.position.events",
    OutboxEventType.POSITION_DELETED: "org.position.events",
}


async def run_outbox_relay(producer: KafkaEventProducer, session_manager: DatabaseSessionManager) -> None:
    while True:
        await asyncio.sleep(1)
        try:
            async with session_manager.session() as session:
                repo = PostgreSQLOutboxEventRepository(session)
                events = await repo.get_unpublished(limit=100)

                for event in events:
                    topic = TOPIC_EVENT_TYPE.get(event.event_type)
                    if topic is None:
                        log.warning("No topic for events", event_type=event.event_type)
                        continue

                    try:
                        await producer.publish(
                            topic=topic,
                            key=str(event.aggregate_id),
                            event=event,
                        )
                    except Exception:
                        log.exception("Failed to publish the event", event_id=str(event.event_id))
                        continue

                    await repo.mark_published(event.event_id)

                await session.commit()

        except Exception:
            log.exception("Outbox relay error")
