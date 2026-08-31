from uuid import UUID

from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.models import StructAdmPositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractListStructAdmPositionUseCase


class PostgreSQLListStructAdmPositionUseCase(AbstractListStructAdmPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: UUID, company_id: UUID) -> list[StructAdmPositionDTO]:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise StructAdmNotFound

            return await uow.struct_adm_position.list_by_struct_adm_id(struct_adm_id=struct_adm_id)
