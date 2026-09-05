from aiokafka import AIOKafkaConsumer, OffsetAndMetadata, TopicPartition


class KafkaEventConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, topics: list[str]):
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topics = topics
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()

    def __aiter__(self):
        return self._consumer.__aiter__()

    async def commit_message(self, message) -> None:
        topic_partition = TopicPartition(
            message.topic,
            message.partition,
        )
        await self._consumer.commit({topic_partition: OffsetAndMetadata(message.offset + 1, "")})
