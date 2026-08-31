from uuid import UUID

from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.models import StructAdmPositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractDeleteStructAdmPositionUseCase


class PostgreSQLDeleteStructAdmPositionUseCase(AbstractDeleteStructAdmPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: StructAdmPositionDTO, company_id: UUID) -> None:
        async with self._uow as uow:
            position = await uow.position.get(position_id=dto.position_id)
            if not position or position.company_id != company_id:
                raise PositionNotFound

            struct_adm = await uow.struct_adm.get(struct_adm_id=dto.struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise StructAdmNotFound

            return await uow.struct_adm_position.delete_by_dto(dto=dto)
