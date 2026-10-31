import asyncio
from contextlib import asynccontextmanager

from sqlalchemy import text

from api.v1.routers import router
from container import Container
from fastapi import FastAPI, Header, Depends
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.correlation import CorrelationIdMiddleware
from infrastructure.kafka.consumer.consumer_loop import run_event_consumer
from infrastructure.kafka.producer.producer_loop import run_outbox_relay
from infrastructure.workers.registration_saga import run_saga_recovery
from logger import get_logger, setup_logging
from settings import settings

container = Container()

log = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.app.debug)
    log.info("Приложение запущено", host=settings.app.host, port=settings.app.port)

    sessionmanager = container.session_manager()
    sessionmanager.init(settings.database.get_database_url())

    async with asyncio.timeout(5):
        async with sessionmanager.session() as session:
            await session.execute(text("SELECT 1"))

    container.wire(
        modules=[
            "infrastructure.databases.postgresql.session",
            # "api.v1.user.dependencies", # добавить, когда появится @inject
        ]
    )

    kafka_producer = container.kafka_producer()
    kafka_consumer = container.kafka_consumer()
    await kafka_producer.start()
    await kafka_consumer.start()

    log.info("PostgreSQL and Kafka are ready, starting the workers.")

    tasks = [
        asyncio.create_task(run_outbox_relay(producer=kafka_producer, session_manager=sessionmanager)),
        asyncio.create_task(run_event_consumer(consumer=kafka_consumer, session_manager=sessionmanager)),
        asyncio.create_task(run_saga_recovery(session_manager=sessionmanager)),
    ]

    try:
        yield

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        await kafka_producer.stop()
        await kafka_consumer.stop()
        await sessionmanager.close()
        log.info("application shutdown")


async def correlation_header(_value: str | None = Header(default=None, alias="X-Correlation-ID")) -> None:
    pass


app = FastAPI(lifespan=lifespan, dependencies=[Depends(correlation_header)],)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(router)