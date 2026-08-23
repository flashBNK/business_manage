from sqlalchemy.ext.asyncio import AsyncSession

from .account.account import PostgreSQLAccountRepository
from .company.company import PostgreSQLCompanyRepository
from .invite.invite import PostgreSQLInviteRepository
from .member.member import PostgreSQLMemberRepository
from .outbox_event.outbox_event import PostgreSQLOutboxEventRepository
from .refresh_token.refresh_token import PostgreSQLRefreshTokenRepository
from .secret.secret import PostgreSQLSecretRepository
from .user.user import PostgreSQLUserRepository


class PostgreSQLUnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

        self.account: PostgreSQLAccountRepository | None = None
        self.invite: PostgreSQLInviteRepository | None = None
        self.secret: PostgreSQLSecretRepository | None = None
        self.member: PostgreSQLMemberRepository | None = None
        self.company: PostgreSQLCompanyRepository | None = None
        self.user: PostgreSQLUserRepository | None = None
        self.refresh_token: PostgreSQLRefreshTokenRepository | None = None
        self.outbox_event: PostgreSQLOutboxEventRepository | None = None

    async def __aenter__(self):
        self.account = PostgreSQLAccountRepository(self._session)
        self.invite = PostgreSQLInviteRepository(self._session)
        self.secret = PostgreSQLSecretRepository(self._session)
        self.member = PostgreSQLMemberRepository(self._session)
        self.company = PostgreSQLCompanyRepository(self._session)
        self.user = PostgreSQLUserRepository(self._session)
        self.refresh_token = PostgreSQLRefreshTokenRepository(self._session)
        self.outbox_event = PostgreSQLOutboxEventRepository(self._session)
        return self

    async def __aexit__(self, exc_type: Exception | None, exc_val, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
        self.account = None
        self.invite = None
        self.secret = None
        self.member = None
        self.company = None
        self.user = None
        self.refresh_token = None
        self.outbox_event = None

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
