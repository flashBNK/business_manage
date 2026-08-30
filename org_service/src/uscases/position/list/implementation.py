from uuid import UUID

from domain.position.models import PositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractListPositionUseCase


class PostgreSQLListPositionUseCase(AbstractListPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID) -> list[PositionDTO]:
        async with self._uow as uow:
            return await uow.position.list(company_id=company_id)
