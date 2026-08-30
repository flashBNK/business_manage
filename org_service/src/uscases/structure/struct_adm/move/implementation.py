import uuid

from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import MoveStructAdmDTO, StructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractMoveStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLMoveStructAdmUseCase(AbstractMoveStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: uuid.UUID, company_id: uuid.UUID, dto: MoveStructAdmDTO) -> StructAdmDTO:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise InvalidRequestStructAdm
            new_parent = await uow.struct_adm.get(struct_adm_id=dto.new_parent_id)
            if not new_parent or new_parent.company_id != company_id:
                raise InvalidRequestStructAdm
            children = await uow.struct_adm.get_descendants(parent_path=struct_adm.path)
            if new_parent in children:
                raise InvalidRequestStructAdm
            new_path = f"{new_parent.path}.n{struct_adm.id.hex}"

            await uow.struct_adm.move_subtree(new_path=new_path, old_path=struct_adm.path)
            return await uow.struct_adm.get(struct_adm_id=struct_adm_id)
