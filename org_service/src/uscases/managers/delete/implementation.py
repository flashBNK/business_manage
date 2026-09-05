from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.struct_adm.models import DeleteManagerStructAdmDTO, ManagerDTO
from domain.users_position.models import GetUsersPositionDTO, UpdateRoleUsersPositionDTO
from infrastructure.databases.postgresql.models.users_position import Role
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractDeleteManagerStructAdmUseCase


class PostgreSQLDeleteManagerStructAdmUseCase(AbstractDeleteManagerStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: DeleteManagerStructAdmDTO, company_id: UUID) -> ManagerDTO:
        correlation_id = uuid4()
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
                    role=Role.MEMBER,
                )
            )

            manager = ManagerDTO(
                user_id=users_position.user_id,
                struct_adm_id=users_position.struct_adm_id,
                position_id=users_position.position_id,
                role=users_position.role,
            )

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_POSITION_CHANGED,
                    aggregate_id=manager.user_id,
                    correlation_id=correlation_id,
                    payload={
                        "user_id": str(manager.user_id),
                        "struct_adm_id": str(manager.struct_adm_id),
                        "company_id": str(company_id),
                        "position_id": str(manager.position_id),
                        "role": str(manager.role),
                    },
                )
            )

            return manager
