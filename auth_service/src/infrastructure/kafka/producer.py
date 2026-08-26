from json import dumps

from aiokafka import AIOKafkaProducer
from domain.outbox_event.models import OutboxEventDTO


class KafkaEventProducer:
    def __init__(self, bootstrap_servers: str):
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers)
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()

    async def publish(self, topic: str, key: str, event: OutboxEventDTO) -> None:
        event_message = {
            "event_id": str(event.event_id),
            "event_type": event.event_type.value,
            "schema_version": event.schema_version,
            "aggregate_id": str(event.aggregate_id),
            "correlation_id": str(event.correlation_id),
            "causation_id": str(event.causation_id) if event.causation_id else None,
            "producer": event.producer,
            "occurred_at": event.occurred_at.isoformat(),
            "payload": event.payload,
        }
        await self._producer.send_and_wait(
            topic=topic,
            key=key.encode(),
            value=dumps(event_message).encode(),
        )
