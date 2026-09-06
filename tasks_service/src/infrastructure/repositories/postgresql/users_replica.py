from uuid import UUID

from domain.users_replica.models import CreateUsersReplicaDTO, UsersReplicaDTO
from domain.users_replica.repository import AbstractUsersReplicaRepository
from infrastructure.databases.postgresql.models.users_replica import UsersReplica as UsersReplicaModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLUsersReplicaRepository(AbstractUsersReplicaRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateUsersReplicaDTO) -> UsersReplicaDTO:
        db_users_replica = UsersReplicaModel(
            id=dto.id,
            username=dto.username,
            company_id=dto.company_id,
            last_event_at=dto.last_event_at,
            is_active=dto.is_active,
        )

        self._session.add(db_users_replica)
        await self._session.flush()

        return self._to_domain(db_users_replica)

    async def upsert(self, dto: CreateUsersReplicaDTO) -> UsersReplicaDTO:
        stmt = insert(UsersReplicaModel).values(
            id=dto.id,
            username=dto.username,
            company_id=dto.company_id,
            last_event_at=dto.last_event_at,
            is_active=dto.is_active,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "username": stmt.excluded.username,
                "company_id": stmt.excluded.company_id,
                "last_event_at": stmt.excluded.last_event_at,
                "is_active": stmt.excluded.is_active,
                "deleted_at": None,
            },
            where=UsersReplicaModel.last_event_at < stmt.excluded.last_event_at,
        ).returning(UsersReplicaModel)

        result = await self._session.execute(stmt)
        user_replica = result.scalar_one_or_none()

        if user_replica is None:
            user_replica = await self._session.scalar(
                select(UsersReplicaModel).where(
                    UsersReplicaModel.id == dto.id,
                )
            )

        return self._to_domain(user_replica)

    async def delete(self, users_replica_id: UUID) -> None:
        pass

    async def get(self, users_replica_id: UUID) -> UsersReplicaDTO | None:
        stmt = select(UsersReplicaModel).where(UsersReplicaModel.id == users_replica_id)
        result = await self._session.execute(stmt)
        users_replica = result.scalar_one_or_none()

        if not users_replica:
            return None

        return self._to_domain(users_replica)

    @staticmethod
    def _to_domain(users_replica: UsersReplicaModel) -> UsersReplicaDTO:
        return UsersReplicaDTO(
            id=users_replica.id,
            company_id=users_replica.company_id,
            username=users_replica.username,
            last_event_at=users_replica.last_event_at,
            is_active=users_replica.is_active,
        )
