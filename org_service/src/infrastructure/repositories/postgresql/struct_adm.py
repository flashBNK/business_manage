from uuid import UUID

from domain.struct_adm.models import CreateStructAdmDTO, StructAdmDTO
from domain.struct_adm.repository import AbstractStructAdmRepository
from infrastructure.databases.postgresql.models.struct_adm import StructAdm as StructAdmModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree


class PostgreSQLStructAdmRepository(AbstractStructAdmRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        db_struct_adm = StructAdmModel(
            company_id=dto.company_id,
            name=dto.name,
            path=dto.path,
            manager_id=dto.manager_id,
        )

        self._session.add(db_struct_adm)
        await self._session.flush()

        return self._to_domain(db_struct_adm)

    async def ensure_root(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        path = Ltree(f"c{dto.company_id.hex}")

        stmt = (
            insert(StructAdmModel)
            .values(company_id=dto.company_id, name=dto.name, path=path, manager_id=dto.manager_id)
            .on_conflict_do_update(index_elements=["path"], set_={"name": dto.name})
            .returning(StructAdmModel)
        )

        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one()

        return self._to_domain(struct_adm)

    async def delete(self, struct_adm_id: UUID) -> None:
        pass

    async def get(self, struct_adm_id: UUID) -> StructAdmDTO | None:
        stmt = select(StructAdmModel).where(StructAdmModel.id == struct_adm_id)
        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one_or_none()

        if not struct_adm:
            return None

        return self._to_domain(struct_adm)

    @staticmethod
    def _to_domain(struct_adm: StructAdmModel) -> StructAdmDTO:
        return StructAdmDTO(
            id=struct_adm.id,
            company_id=struct_adm.company_id,
            name=struct_adm.name,
            path=str(struct_adm.path),
            manager_id=struct_adm.manager_id,
        )
