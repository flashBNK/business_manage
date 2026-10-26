from uuid import UUID

from domain.position.models import CreatePositionDTO, PositionDTO, UpdatePositionDTO
from domain.position.repository import AbstractPositionRepository
from infrastructure.databases.postgresql.models.position import Position as PositionModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLPositionRepository(AbstractPositionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreatePositionDTO) -> PositionDTO:
        db_position = PositionModel(company_id=dto.company_id, name=dto.name, description=dto.description)

        self._session.add(db_position)
        await self._session.flush()

        return self._to_domain(db_position)

    async def delete(self, position_id: UUID) -> None:
        stmt = select(PositionModel).where(PositionModel.id == position_id)
        result = await self._session.execute(stmt)
        position = result.scalar_one_or_none()

        if not position:
            return None

        await self._session.delete(position)
        await self._session.flush()

    async def get(self, position_id: UUID) -> PositionDTO | None:
        stmt = select(PositionModel).where(PositionModel.id == position_id)
        result = await self._session.execute(stmt)
        position = result.scalar_one_or_none()

        if not position:
            return None

        return self._to_domain(position)

    async def list_paginated(self, company_id: UUID, limit: int, offset: int) -> tuple[list[PositionDTO], int]:
        total_stmt = select(func.count()).select_from(PositionModel).where(PositionModel.company_id == company_id)
        total_result = await self._session.execute(total_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(PositionModel)
            .where(PositionModel.company_id == company_id)
            .order_by(PositionModel.name.asc(), PositionModel.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        positions = result.scalars().all()

        return [self._to_domain(position) for position in positions], total or 0

    async def update(self, position_id: UUID, dto=UpdatePositionDTO) -> PositionDTO | None:
        stmt = select(PositionModel).where(PositionModel.id == position_id)
        result = await self._session.execute(stmt)
        position = result.scalar_one_or_none()

        if not position:
            return None

        if dto.description:
            position.description = dto.description
        if dto.name:
            position.name = dto.name

        self._session.add(position)
        await self._session.flush()

        return self._to_domain(position)

    @staticmethod
    def _to_domain(struct_adm: PositionModel) -> PositionDTO:
        return PositionDTO(
            id=struct_adm.id,
            company_id=struct_adm.company_id,
            name=struct_adm.name,
            description=struct_adm.description,
        )
