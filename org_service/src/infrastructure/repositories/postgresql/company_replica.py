from uuid import UUID

from domain.company_replica.models import CompanyReplicaDTO, CreateCompanyReplicaDTO
from domain.company_replica.repository import AbstractCompanyReplicaRepository
from infrastructure.databases.postgresql.models.company_replica import CompanyReplica as CompanyReplicaModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLCompanyReplicaRepository(AbstractCompanyReplicaRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateCompanyReplicaDTO) -> CompanyReplicaDTO:
        db_company_replica = CompanyReplicaModel(
            name=dto.name,
        )

        self._session.add(db_company_replica)
        await self._session.flush()

        return self._to_domain(db_company_replica)

    async def upsert(self, dto: CreateCompanyReplicaDTO) -> CompanyReplicaDTO:
        stmt = (
            insert(CompanyReplicaModel)
            .values(id=dto.company_id, name=dto.name)
            .on_conflict_do_update(index_elements=["id"], set_={"name": dto.name})
            .returning(CompanyReplicaModel)
        )

        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one()

        return self._to_domain(struct_adm)

    async def delete(self, company_replica: UUID) -> None:
        pass

    async def get(self, company_replica_id: UUID) -> CompanyReplicaDTO | None:
        stmt = select(CompanyReplicaModel).where(CompanyReplicaModel.id == company_replica_id)
        result = await self._session.execute(stmt)
        company_replica = result.scalar_one_or_none()

        if not company_replica:
            return None

        return self._to_domain(company_replica)

    @staticmethod
    def _to_domain(company_replica: CompanyReplicaModel) -> CompanyReplicaDTO:
        return CompanyReplicaDTO(
            id=company_replica.id,
            name=company_replica.name,
        )
