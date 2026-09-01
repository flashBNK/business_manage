import uuid

from domain.company_replica.exceptions import CompanyReplicaNotFound
from domain.struct_adm.models import CompanyStructureDTO, StructAdmTreeDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

from .abstract import AbstractGetCompanyStructureUseCase

log = get_logger(__name__)


class PostgreSQLGetCompanyStructureUseCase(AbstractGetCompanyStructureUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: uuid.UUID) -> CompanyStructureDTO:
        async with self._uow as uow:
            company = await uow.company_replica.get(company_replica_id=company_id)
            if not company:
                raise CompanyReplicaNotFound

            list_tree = await uow.struct_adm.list_tree(company_id=company_id)

            tree_struct_adm = {
                struct_adm.path: StructAdmTreeDTO(
                    id=struct_adm.id,
                    name=struct_adm.name,
                    path=struct_adm.path,
                    manager_id=struct_adm.manager_id,
                )
                for struct_adm in list_tree
            }
            roots: list[StructAdmTreeDTO] = []

            for struct_adm in list_tree:
                current = tree_struct_adm[struct_adm.path]
                if "." not in struct_adm.path:
                    roots.append(current)
                    continue

                parent_path = struct_adm.path.rsplit(".", 1)[0]
                parent = tree_struct_adm.get(parent_path)
                if parent:
                    parent.children.append(current)

            return CompanyStructureDTO(
                id=company.id,
                name=company.name,
                children=roots,
            )
