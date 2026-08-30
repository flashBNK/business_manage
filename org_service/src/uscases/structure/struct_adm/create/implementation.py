import uuid

from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import CreateStructAdmDTO, StructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractCreateStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLCreateStructAdmUseCase(AbstractCreateStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateStructAdmDTO, parent_id: uuid.UUID) -> StructAdmDTO:
        async with self._uow as uow:
            parent = await uow.struct_adm.get(struct_adm_id=parent_id)
            if not parent:
                raise InvalidRequestStructAdm

            path = f"{parent.path}.n{dto.id.hex}"
            dto.path = path

            struct_adm_dto = CreateStructAdmDTO(
                id=dto.id,
                company_id=parent.company_id,
                name=dto.name,
                path=path,
                manager_id=dto.manager_id,
            )

            return await uow.struct_adm.create(dto=struct_adm_dto)
