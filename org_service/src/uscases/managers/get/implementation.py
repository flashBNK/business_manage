from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm.models import ManagerDTO
from domain.users_position.exceptions import UsersPositionNotFound
from domain.users_position.models import GetManagerDTO, GetManagerPositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractGetManagerStructAdmUseCase


class PostgreSQLGetManagerStructAdmUseCase(AbstractGetManagerStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: GetManagerDTO) -> ManagerDTO:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=dto.struct_adm_id)
            if struct_adm is None or struct_adm.company_id != dto.company_id:
                raise StructAdmNotFound
            users_position = await uow.users_position.get_manager(
                dto=GetManagerPositionDTO(
                    struct_adm_id=struct_adm.id,
                )
            )
            if not users_position:
                raise UsersPositionNotFound

            return ManagerDTO(
                user_id=users_position.user_id,
                struct_adm_id=struct_adm.id,
                position_id=users_position.position_id,
                role=users_position.role,
            )
