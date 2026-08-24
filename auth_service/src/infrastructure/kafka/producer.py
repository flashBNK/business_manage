from json import dumps

from aiokafka import AIOKafkaProducer

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


    async def publish(self, topic: str, key: str, value: dict) -> None:
        await self._producer.send_and_wait(
            topic=topic,
            key=key.encode(),
            value=dumps(value, default=str).encode(),
        )