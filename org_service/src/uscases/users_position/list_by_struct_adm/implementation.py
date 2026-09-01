from uuid import UUID

from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm.models import StructAdmDTO
from domain.users_position.models import EmployeePositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractListUsersPositionByStructAdmUseCase


class PostgreSQLListUsersPositionByStructAdmUseCase(AbstractListUsersPositionByStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(
        self, struct_adm_id: UUID, company_id: UUID, include_children: bool = False
    ) -> tuple[list[EmployeePositionDTO], StructAdmDTO]:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise StructAdmNotFound

            employees = await uow.users_position.list_by_struct_adm(
                struct_adm_id=struct_adm_id,
                company_id=company_id,
                include_children=include_children,
                struct_adm_path=struct_adm.path,
            )

            return employees, struct_adm
