from collections.abc import AsyncIterator

from container import Container
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager
from sqlalchemy.ext.asyncio import AsyncSession


@inject
async def get_async_session(
    session_manager: DatabaseSessionManager = Depends(Provide[Container.session_manager]),
) -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session
