import uuid

from domain.struct_adm.exceptions import InvalidRequestStructAdm
from domain.struct_adm.models import StructAdmDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractGetAncestorsStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLGetAncestorsUseCase(AbstractGetAncestorsStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: uuid.UUID, company_id: uuid.UUID) -> list[StructAdmDTO]:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm:
                raise InvalidRequestStructAdm
            if struct_adm.company_id != company_id:
                raise InvalidRequestStructAdm

            return await uow.struct_adm.get_ancestors(struct_adm_path=struct_adm.path)
