from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.exceptions import StructAdmPositionNotFound
from domain.struct_adm_position.models import CreateStructAdmPositionDTO
from domain.users_position.models import CreateUsersPositionDTO, UsersPositionDTO
from domain.users_replica.exceptions import UsersReplicaNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractCreateUsersPositionUseCase


class PostgreSQLCreateUsersPositionUseCase(AbstractCreateUsersPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateUsersPositionDTO, company_id: UUID) -> UsersPositionDTO:
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

            struct_adm_position = await uow.struct_adm_position.get_by_pair(
                dto=CreateStructAdmPositionDTO(position_id=dto.position_id, struct_adm_id=dto.struct_adm_id)
            )
            if not struct_adm_position:
                raise StructAdmPositionNotFound

            users_position = await uow.users_position.create(dto=dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_POSITION_CHANGED,
                    aggregate_id=user.id,
                    correlation_id=correlation_id,
                    payload={
                        "user_id": str(users_position.user_id),
                        "struct_adm_id": str(users_position.struct_adm_id),
                        "company_id": str(struct_adm.company_id),
                        "position_id": str(users_position.position_id),
                        "role": str(users_position.role),
                    },
                )
            )

            return users_position