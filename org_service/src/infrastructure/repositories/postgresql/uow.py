from infrastructure.repositories.postgresql.company_replica import PostgreSQLCompanyReplicaRepository
from infrastructure.repositories.postgresql.inbox_event import PostgreSQLInboxEventRepository
from infrastructure.repositories.postgresql.position import PostgreSQLPositionRepository
from infrastructure.repositories.postgresql.struct_adm import PostgreSQLStructAdmRepository
from infrastructure.repositories.postgresql.struct_adm_position import PostgreSQLStructAdmPositionRepository
from infrastructure.repositories.postgresql.users_position import PostgreSQLUsersPositionRepository
from infrastructure.repositories.postgresql.users_replica import PostgreSQLUsersReplicaRepository
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLOrgUnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

        self.struct_adm: PostgreSQLStructAdmRepository | None = None
        self.company_replica: PostgreSQLCompanyReplicaRepository | None = None
        self.users_replica: PostgreSQLUsersReplicaRepository | None = None
        self.inbox_event: PostgreSQLInboxEventRepository | None = None
        self.position: PostgreSQLPositionRepository | None = None
        self.struct_adm_position: PostgreSQLStructAdmPositionRepository | None = None
        self.users_position: PostgreSQLUsersPositionRepository | None = None

    async def __aenter__(self):
        self.struct_adm = PostgreSQLStructAdmRepository(session=self._session)
        self.company_replica = PostgreSQLCompanyReplicaRepository(session=self._session)
        self.users_replica = PostgreSQLUsersReplicaRepository(session=self._session)
        self.inbox_event = PostgreSQLInboxEventRepository(session=self._session)
        self.position = PostgreSQLPositionRepository(session=self._session)
        self.struct_adm_position = PostgreSQLStructAdmPositionRepository(session=self._session)
        self.users_position = PostgreSQLUsersPositionRepository(session=self._session)

        return self

    async def __aexit__(self, exc_type: Exception | None, exc_val, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
        self.struct_adm = None
        self.company_replica = None
        self.users_replica = None
        self.inbox_event = None
        self.position = None
        self.struct_adm_position = None
        self.users_position = None

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
