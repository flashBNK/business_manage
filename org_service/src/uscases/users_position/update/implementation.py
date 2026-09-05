from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.exceptions import StructAdmPositionNotFound
from domain.struct_adm_position.models import CreateStructAdmPositionDTO
from domain.users_position.models import (
    GetUsersPositionDTO,
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractUpdateUsersPositionUseCase
from logger import get_logger

log = get_logger(__name__)


class PostgreSQLUpdateUsersPositionUseCase(AbstractUpdateUsersPositionUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: UpdateUsersPositionDTO, company_id: UUID) -> UsersPositionDTO:
        correlation_id = uuid4()

        async with self._uow as uow:
            log.info("Start update user position")
            await uow.users_position.get_for_check(
                dto=GetUsersPositionDTO(
                    user_id=dto.user_id, struct_adm_id=dto.old_struct_adm_id, position_id=dto.old_position_id
                ),
                company_id=company_id,
            )
            log.info("Check users_position")

            struct_adm_position = await uow.struct_adm_position.get_by_pair(
                dto=CreateStructAdmPositionDTO(position_id=dto.old_position_id, struct_adm_id=dto.old_struct_adm_id)
            )
            if not struct_adm_position:
                raise StructAdmPositionNotFound
            log.info("Check struct_adm_position")

            if dto.new_struct_adm_id:
                new_struct_adm = await uow.struct_adm.get(struct_adm_id=dto.new_struct_adm_id)
                if not new_struct_adm or new_struct_adm.company_id != company_id:
                    raise StructAdmNotFound

            if dto.new_position_id:
                new_position = await uow.position.get(position_id=dto.new_position_id)
                if not new_position or new_position.company_id != company_id:
                    raise PositionNotFound

            users_position = await uow.users_position.update(dto=dto)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_POSITION_CHANGED,
                    aggregate_id=users_position.user_id,
                    correlation_id=correlation_id,
                    payload={
                        "user_id": str(users_position.user_id),
                        "struct_adm_id": str(users_position.struct_adm_id),
                        "company_id": str(company_id),
                        "position_id": str(users_position.position_id),
                        "role": str(users_position.role),
                    },
                )
            )

            return users_position

