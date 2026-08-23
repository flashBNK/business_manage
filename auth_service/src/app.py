from contextlib import asynccontextmanager

from api.v1.routers import router
from container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
            # "api.v1.user.dependencies",  # добавить сюда, когда там появится @inject
        ]
    )

    try:
        yield

    finally:
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
