from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.exceptions import StructAdmPositionNotFound
from domain.struct_adm_position.models import CreateStructAdmPositionDTO
from domain.users_position.create_helper import assign_employee
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
            return await assign_employee(uow=uow, dto=dto, company_id=company_id, correlation_id=correlation_id)
