from uuid import UUID

from domain.struct_adm.models import AddManagerStructAdmDTO, ManagerDTO
from domain.users_position.models import GetUsersPositionDTO, UpdateRoleUsersPositionDTO
from infrastructure.databases.postgresql.models.users_position import Role
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractAddManagerStructAdmUseCase


class PostgreSQLAddManagerStructAdmUseCase(AbstractAddManagerStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: AddManagerStructAdmDTO, company_id: UUID) -> ManagerDTO:
        async with self._uow as uow:
            old_users_position = await uow.users_position.get_for_check(
                dto=GetUsersPositionDTO(
                    user_id=dto.user_id, struct_adm_id=dto.struct_adm_id, position_id=dto.position_id
                ),
                company_id=company_id,
            )

            users_position = await uow.users_position.update_role(
                dto=UpdateRoleUsersPositionDTO(
                    user_id=old_users_position.user_id,
                    struct_adm_id=old_users_position.struct_adm_id,
                    position_id=old_users_position.position_id,
                    role=Role.MANAGER,
                )
            )

            struct_adm = await uow.struct_adm.add_manager(dto=dto)

            return ManagerDTO(
                user_id=struct_adm.manager_id,
                struct_adm_id=struct_adm.id,
                position_id=users_position.position_id,
                role=users_position.role,
            )
