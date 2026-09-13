import asyncio

from domain.outbox_event.models import OutboxEventType
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.kafka.producer.producer import KafkaEventProducer
from infrastructure.repositories.postgresql.outbox_event.outbox_event import PostgreSQLOutboxEventRepository
from logger import get_logger

log = get_logger(__name__)

TOPIC_EVENT_TYPE = {
    OutboxEventType.COMPANY_CREATED: "auth.company.events",
    OutboxEventType.EMPLOYEE_CREATED: "auth.employee.events",
    OutboxEventType.EMPLOYEE_REGISTERED: "auth.employee.events",
    OutboxEventType.EMPLOYEE_REGISTRATION_FAILED: "auth.employee.events",
    OutboxEventType.REGISTRATION_ORG_PROVISION: "registration.org.commands",
    OutboxEventType.REGISTRATION_ORG_COMPENSATE: "registration.org.commands",
    OutboxEventType.REGISTRATION_TASKS_PROVISION: "registration.tasks.commands",
    OutboxEventType.REGISTRATION_ORG_COMPLETED: "registration.saga.events",
    OutboxEventType.REGISTRATION_ORG_FAILED: "registration.saga.events",
    OutboxEventType.REGISTRATION_ORG_COMPENSATED: "registration.saga.events",
    OutboxEventType.REGISTRATION_TASKS_COMPLETED: "registration.saga.events",
    OutboxEventType.REGISTRATION_TASKS_FAILED: "registration.saga.events",
    OutboxEventType.REGISTRATION_COMPLETED: "registration.saga.events",
    OutboxEventType.REGISTRATION_FAILED: "registration.saga.events",
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
                        log.warning("Нет топика для события", event_type=event.event_type)
                        continue

                    try:
                        await producer.publish(
                            topic=topic,
                            key=str(event.aggregate_id),
                            event=event,
                        )
                    except Exception:
                        log.exception("Не удалось опубликовать событие", event_id=str(event.event_id))
                        continue

                    await repo.mark_published(event.event_id)

                await session.commit()

        except Exception:
            log.exception("Ошибка в outbox relay")
