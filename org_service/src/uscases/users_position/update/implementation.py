from uuid import UUID

from domain.struct_adm.exceptions import StructAdmNotFound
from domain.users_position.models import (
    GetUsersPositionDTO,
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractUpdateUsersPositionUseCase


class PostgreSQLUpdateUsersPositionUseCase(AbstractUpdateUsersPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: UpdateUsersPositionDTO, company_id: UUID) -> UsersPositionDTO:
        async with self._uow as uow:
            await uow.users_position.get_for_check(
                dto=GetUsersPositionDTO(
                    user_id=dto.user_id, struct_adm_id=dto.old_struct_adm_id, position_id=dto.old_position_id
                ),
                company_id=company_id,
            )

            if dto.new_struct_adm_id:
                new_struct_adm = await uow.struct_adm.get(struct_adm_id=dto.new_struct_adm_id)
                if not new_struct_adm or new_struct_adm.company_id != company_id:
                    raise StructAdmNotFound

            if dto.new_position_id:
                new_position = await uow.position.get(position_id=dto.new_position_id)
                if not new_position or new_position.company_id != company_id:
                    raise StructAdmNotFound

            return await uow.users_position.update(dto=dto)
