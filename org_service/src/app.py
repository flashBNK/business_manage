import asyncio
import contextlib
from contextlib import asynccontextmanager

from api.v1.routers import router
from container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from infrastructure.kafka.relay import run_outbox_relay
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

    container.wire(
        modules=[
            "infrastructure.databases.postgresql.session",
            # "api.v1.user.dependencies", # добавить, когда появится @inject
        ]
    )

    # kafka_producer = container.kafka_producer()
    # await kafka_producer.start()
    #
    # relay_task = asyncio.create_task(run_outbox_relay(producer=kafka_producer, session_manager=sessionmanager))

    try:
        yield

    finally:
        # relay_task.cancel()
        # with contextlib.suppress(asyncio.CancelledError):
        #     await relay_task
        # await kafka_producer.stop()
        await sessionmanager.close()
        log.info("application shutdown")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
