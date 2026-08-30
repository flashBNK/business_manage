from uuid import UUID

from domain.position.exceptions import PositionNotFound
from domain.position.models import PositionDTO, UpdatePositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractUpdatePositionUseCase


class PostgreSQLUpdatePositionUseCase(AbstractUpdatePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: UpdatePositionDTO, company_id: UUID, position_id: UUID) -> PositionDTO:
        async with self._uow as uow:
            position = await uow.position.get(position_id=position_id)

            if not position or position.company_id != company_id:
                raise PositionNotFound

            return await uow.position.update(dto=dto, position_id=position_id)
