from sqlalchemy.ext.asyncio import AsyncSession

from .account.account import PostgreSQLAccountRepository
from .invite.invite import PostgreSQLInviteRepository


class PostgreSQLUnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

        self.account: PostgreSQLAccountRepository | None = None
        self.invite: PostgreSQLInviteRepository | None = None

    async def __aenter__(self):
        self.account = PostgreSQLAccountRepository(self._session)
        self.invite = PostgreSQLInviteRepository(self._session)
        return self

    async def __aexit__(self, exc_type: Exception | None, exc_val, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
        self.account = None
        self.invite = None

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()