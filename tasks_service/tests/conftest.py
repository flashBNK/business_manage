import os
from pathlib import Path

import pytest_asyncio
from app import app
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from infrastructure.databases.postgresql.base import Base
from infrastructure.databases.postgresql.session import get_async_session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

pytest_plugins = ("tests.fixtures.auth",)

ROOT = Path(__file__).resolve().parents[1]
ENV_TEST_PATH = ROOT / "config" / ".env.test"
if not ENV_TEST_PATH.exists():
    raise FileNotFoundError(f"Test env file not found: {ENV_TEST_PATH}")
load_dotenv(ENV_TEST_PATH)


@pytest_asyncio.fixture(scope="session")
async def engine():
    database_url = os.environ["DATABASE_URL"]

    engine = create_async_engine(database_url, echo=False, poolclass=NullPool)

    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS ltree"))
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture()
async def session(engine):
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_database(engine):
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE TABLE
                    outbox_event,
                    inbox_event,
                    task,
                    task_assignees,
                    task_watchers,
                    users_replica
                RESTART IDENTITY CASCADE
                """
            )
        )
    yield


@pytest_asyncio.fixture()
async def client(session):
    async def override_get_async_session():
        yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
