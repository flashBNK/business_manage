from uuid import UUID

from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm.models import StructAdmDTO
from domain.users_position.models import ListResponseEmployeePositionDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork

from .abstract import AbstractListUsersPositionByStructAdmUseCase


class PostgreSQLListUsersPositionByStructAdmUseCase(AbstractListUsersPositionByStructAdmUseCase):
    def __init__(self, uow: PostgreSQLOrgUnitOfWork):
        self._uow = uow

    async def execute(
        self, struct_adm_id: UUID, company_id: UUID, include_children: bool, limit: int, offset: int
    ) -> tuple[ListResponseEmployeePositionDTO, StructAdmDTO]:
        async with self._uow as uow:
            struct_adm = await uow.struct_adm.get(struct_adm_id=struct_adm_id)
            if not struct_adm or struct_adm.company_id != company_id:
                raise StructAdmNotFound

            employees, total = await uow.users_position.list_paginated_by_struct_adm(
                struct_adm_id=struct_adm_id,
                company_id=company_id,
                struct_adm_path=struct_adm.path,
                include_children=include_children,
                limit=limit,
                offset=offset,
            )

            return (
                ListResponseEmployeePositionDTO(total=total, employees=employees, limit=limit, offset=offset),
                struct_adm,
            )
