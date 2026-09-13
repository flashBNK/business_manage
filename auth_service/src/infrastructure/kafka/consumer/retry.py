import asyncio

from domain.inbox_event.models import CreateInboxEventDTO
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from infrastructure.di.injection import build_unit_of_work
from logger import get_logger

log = get_logger(__name__)

MAX_ATTEMPTS = 3
BASE_RETRY_DELAY = 1.0


async def process_event_with_retry(
    event: EventEnvelopeDTO,
    handler,
    session_manager: DatabaseSessionManager,
    consumer_name: str,
) -> bool:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async with session_manager.session() as session:
                async with build_unit_of_work(session=session) as uow:
                    await handler(event=event, uow=uow)

                    await uow.inbox_event.create(
                        CreateInboxEventDTO(consumer_name=consumer_name, event_id=event.event_id)
                    )

                    log.info(
                        "Kafka event processed successfully",
                        event_id=event.event_id,
                        event_type=event.event_type,
                        attempt=attempt,
                    )
                    return True
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception(
                "Kafka event processing failed",
                event_id=event.event_id,
                event_type=event.event_type,
                attempt=attempt,
                max_attempts=MAX_ATTEMPTS,
            )

            if attempt >= MAX_ATTEMPTS:
                return False

            delay = BASE_RETRY_DELAY * (2 ** (attempt - 1))

            log.info("Retrying Kafka event", event_id=event.event_id, retry_in=delay)
            await asyncio.sleep(delay)

    return False
