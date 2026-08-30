import uuid

from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import StructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractGetChildrenStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLGetChildrenUseCase(AbstractGetChildrenStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, parent_id: uuid.UUID, company_id: uuid.UUID) -> list[StructAdmDTO]:
        async with self._uow as uow:
            parent = await uow.struct_adm.get(struct_adm_id=parent_id)
            if not parent:
                raise InvalidRequestStructAdm
            if parent.company_id != company_id:
                raise InvalidRequestStructAdm

            return await uow.struct_adm.get_children(parent_path=parent.path)
