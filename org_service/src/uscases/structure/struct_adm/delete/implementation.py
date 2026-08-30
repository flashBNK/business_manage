import uuid

from domain.struct_adm.exceptions import InvalidRequestStructAdm
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractDeleteStructAdmUseCase

log = get_logger(__name__)


class PostgreSQLDeleteStructAdmUseCase(AbstractDeleteStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, struct_adm_id: uuid.UUID, company_id: uuid.UUID) -> None:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm:
                return None
            if struct_adm.company_id != company_id:
                raise InvalidRequestStructAdm

            return await uow.struct_adm.delete(struct_adm_id=struct_adm_id)
