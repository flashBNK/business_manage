from domain.position.models import CreatePositionDTO, PositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractCreatePositionUseCase


class PostgreSQLCreatePositionUseCase(AbstractCreatePositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreatePositionDTO) -> PositionDTO:
        async with self._uow as uow:
            return await uow.position.create(dto=dto)
