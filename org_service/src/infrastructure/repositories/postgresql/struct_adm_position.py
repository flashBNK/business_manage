from uuid import UUID

from domain.struct_adm_position.models import CreateStructAdmPositionDTO, StructAdmPositionDTO
from domain.struct_adm_position.repository import AbstractStructAdmPositionRepository
from infrastructure.databases.postgresql.models.struct_adm_position import StructAdmPosition as StructAdmPositionModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLStructAdmPositionRepository(AbstractStructAdmPositionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateStructAdmPositionDTO) -> StructAdmPositionDTO:
        db_struct_adm_position = StructAdmPositionModel(struct_adm_id=dto.struct_adm_id, position_id=dto.position_id)

        self._session.add(db_struct_adm_position)
        await self._session.flush()

        return self._to_domain(db_struct_adm_position)

    async def get_by_pair(self, dto: CreateStructAdmPositionDTO) -> StructAdmPositionDTO | None:
        stmt = (
            select(StructAdmPositionModel)
            .where(StructAdmPositionModel.struct_adm_id == dto.struct_adm_id)
            .where(StructAdmPositionModel.position_id == dto.position_id)
        )
        result = await self._session.execute(stmt)
        struct_adm_position = result.scalar_one_or_none()
        if not struct_adm_position:
            return None
        return self._to_domain(struct_adm_position)

    async def delete_by_dto(self, dto: StructAdmPositionDTO) -> None:
        stmt = (
            select(StructAdmPositionModel)
            .where(StructAdmPositionModel.struct_adm_id == dto.struct_adm_id)
            .where(StructAdmPositionModel.position_id == dto.position_id)
        )
        result = await self._session.execute(stmt)
        struct_adm_position = result.scalar_one_or_none()

        if not struct_adm_position:
            return None

        await self._session.delete(struct_adm_position)
        await self._session.flush()

    async def delete(self, struct_adm_position_id: UUID) -> None:
        pass

    async def list_by_struct_adm_id(
        self, struct_adm_id: UUID, limit: int, offset: int
    ) -> tuple[list[StructAdmPositionDTO], int]:
        total_stmt = (
            select(func.count())
            .select_from(StructAdmPositionModel)
            .where(StructAdmPositionModel.struct_adm_id == struct_adm_id)
        )
        total = await self._session.scalar(total_stmt)

        stmt = (
            select(StructAdmPositionModel)
            .where(StructAdmPositionModel.struct_adm_id == struct_adm_id)
            .order_by(StructAdmPositionModel.position_id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        struct_adm_positions = result.scalars().all()

        return [self._to_domain(struct_adm_position) for struct_adm_position in struct_adm_positions], total or 0

    async def list_by_position_id(self, position_id: UUID) -> list[StructAdmPositionDTO]:
        stmt = select(StructAdmPositionModel).where(StructAdmPositionModel.position_id == position_id)
        result = await self._session.execute(stmt)
        struct_adm_positions = result.scalars().all()

        if not struct_adm_positions:
            return []

        return [self._to_domain(struct_adm_position) for struct_adm_position in struct_adm_positions]

    async def get(self, struct_adm_position_id: UUID) -> StructAdmPositionDTO | None:
        pass

    @staticmethod
    def _to_domain(struct_adm_position: StructAdmPositionModel) -> StructAdmPositionDTO:
        return StructAdmPositionDTO(
            struct_adm_id=struct_adm_position.struct_adm_id,
            position_id=struct_adm_position.position_id,
        )
