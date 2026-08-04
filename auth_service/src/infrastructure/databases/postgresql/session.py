from typing import AsyncIterator

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from container import Container
from infrastructure.databases.postgresql.session_manager import DatabaseSessionManager


@inject
async def get_async_session(
    session_manager: DatabaseSessionManager = Depends(Provide[Container.session_manager]),
) -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session