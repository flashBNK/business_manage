from uuid import UUID

from domain.position.exceptions import PositionNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractDeletePositionUseCase


class PostgreSQLDeletePositionUseCase(AbstractDeletePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, position_id: UUID) -> None:
        async with self._uow as uow:
            position = await uow.position.get(position_id=position_id)

            if not position or position.company_id != company_id:
                raise PositionNotFound

            await uow.position.delete(position_id=position_id)
