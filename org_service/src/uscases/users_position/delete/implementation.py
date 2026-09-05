from uuid import UUID, uuid4

from domain.outbox_event.models import OutboxEventType, CreateOutboxEventDTO
from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.users_position.models import GetUsersPositionDTO, UsersPositionDTO
from domain.users_replica.exceptions import UsersReplicaNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractDeleteUsersPositionUseCase


class PostgreSQLDeleteUsersPositionUseCase(AbstractDeleteUsersPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: GetUsersPositionDTO, company_id: UUID) -> None:
        correlation_id = uuid4()
        async with self._uow as uow:
            position = await uow.position.get(position_id=dto.position_id)
            if not position or position.company_id != company_id:
                raise PositionNotFound

            struct_adm = await uow.struct_adm.get(struct_adm_id=dto.struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise StructAdmNotFound

            user = await uow.users_replica.get(users_replica_id=dto.user_id)
            if not user or user.company_id != company_id:
                raise UsersReplicaNotFound

            await uow.users_position.delete_by_dto(dto=dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_POSITION_DELETED,
                    aggregate_id=user.id,
                    correlation_id=correlation_id,
                    payload={
                        "user_id": str(user.id),
                        "struct_adm_id": str(struct_adm.id),
                        "company_id": str(company_id),
                        "position_id": str(position.id),
                    },
                )
            )

            return None