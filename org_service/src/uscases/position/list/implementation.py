from uuid import UUID

from domain.position.models import ListResponsePositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractListPositionUseCase


class PostgreSQLListPositionUseCase(AbstractListPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, limit: int, offset: int) -> ListResponsePositionDTO:
        async with self._uow as uow:
            positions, total = await uow.position.list_paginated(company_id=company_id, limit=limit, offset=offset)

            return ListResponsePositionDTO(total=total, positions=positions, limit=limit, offset=offset)
