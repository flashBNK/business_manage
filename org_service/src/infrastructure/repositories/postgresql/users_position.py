from uuid import UUID

from domain.users_position.exceptions import UsersPositionNotFound
from domain.users_position.models import (
    CreateUsersPositionDTO,
    EmployeePositionDTO,
    GetManagerPositionDTO,
    GetUsersPositionDTO,
    UpdateRoleUsersPositionDTO,
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)
from domain.users_position.repository import AbstractUsersPositionRepository
from infrastructure.databases.postgresql.models.position import Position as PositionModel
from infrastructure.databases.postgresql.models.struct_adm import StructAdm as StructAdmModel
from infrastructure.databases.postgresql.models.users_position import Role
from infrastructure.databases.postgresql.models.users_position import UsersPosition as UsersPositionModel
from infrastructure.databases.postgresql.models.users_replica import UsersReplica as UsersReplicaModel
from infrastructure.repositories.postgresql.struct_adm import LtreeSQLType
from sqlalchemy import cast, literal, select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLUsersPositionRepository(AbstractUsersPositionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateUsersPositionDTO) -> UsersPositionDTO:
        db_users_position = UsersPositionModel(
            user_id=dto.user_id,
            struct_adm_id=dto.struct_adm_id,
            position_id=dto.position_id,
        )

        self._session.add(db_users_position)
        await self._session.flush()

        return self._to_domain(db_users_position)

    async def delete_by_dto(self, dto: UsersPositionDTO) -> None:
        stmt = (
            select(UsersPositionModel)
            .where(UsersPositionModel.struct_adm_id == dto.struct_adm_id)
            .where(UsersPositionModel.position_id == dto.position_id)
            .where(UsersPositionModel.user_id == dto.user_id)
        )
        result = await self._session.execute(stmt)
        users_position = result.scalar_one_or_none()

        if not users_position:
            return None

        await self._session.delete(users_position)
        await self._session.flush()

    async def delete(self, struct_adm_position_id: UUID) -> None:
        pass

    async def list_by_struct_adm(
        self, struct_adm_id: UUID, company_id: UUID, struct_adm_path: str, include_children: bool = False
    ) -> list[EmployeePositionDTO]:
        stmt = (
            select(
                UsersReplicaModel.id.label("user_id"),
                UsersReplicaModel.username,
                PositionModel.id.label("position_id"),
                PositionModel.name.label("position_name"),
                UsersPositionModel.role,
            )
            .join(UsersReplicaModel, UsersReplicaModel.id == UsersPositionModel.user_id)
            .join(PositionModel, PositionModel.id == UsersPositionModel.position_id)
            .join(StructAdmModel, StructAdmModel.id == UsersPositionModel.struct_adm_id)
            .where(
                StructAdmModel.company_id == company_id,
                UsersReplicaModel.company_id == company_id,
            )
        )

        if include_children:
            struct_adm_path_expr = cast(literal(struct_adm_path), LtreeSQLType())
            stmt = stmt.where(StructAdmModel.path.op("<@")(struct_adm_path_expr))
        else:
            stmt = stmt.where(StructAdmModel.id == struct_adm_id)

        result = await self._session.execute(stmt)
        db_employees = result.all()

        if not db_employees:
            return []

        employees = [
            EmployeePositionDTO(
                user_id=user_id,
                username=username,
                position_id=position_id,
                position_name=position_name,
                role=role,
            )
            for user_id, username, position_id, position_name, role in db_employees
        ]

        return employees

    async def list_by_position(self, company_id: UUID, position_id: UUID) -> list[EmployeePositionDTO]:
        stmt = (
            select(
                UsersReplicaModel.id.label("user_id"),
                UsersReplicaModel.username,
                PositionModel.id.label("position_id"),
                PositionModel.name.label("position_name"),
                UsersPositionModel.role,
            )
            .join(UsersReplicaModel, UsersReplicaModel.id == UsersPositionModel.user_id)
            .join(PositionModel, PositionModel.id == UsersPositionModel.position_id)
            .join(StructAdmModel, StructAdmModel.id == UsersPositionModel.struct_adm_id)
            .where(
                StructAdmModel.company_id == company_id,
                UsersReplicaModel.company_id == company_id,
                PositionModel.id == position_id,
                UsersPositionModel.position_id == position_id,
            )
        )

        result = await self._session.execute(stmt)
        db_employees = result.all()

        if not db_employees:
            return []

        employees = [
            EmployeePositionDTO(
                user_id=user_id,
                username=username,
                position_id=position_id,
                position_name=position_name,
                role=role,
            )
            for user_id, username, position_id, position_name, role in db_employees
        ]

        return employees

    async def get(self, struct_adm_position_id: UUID) -> UsersPositionDTO | None:
        pass

    async def update(self, dto: UpdateUsersPositionDTO) -> UsersPositionDTO:
        stmt = (
            select(UsersPositionModel)
            .where(UsersPositionModel.struct_adm_id == dto.old_struct_adm_id)
            .where(UsersPositionModel.position_id == dto.old_position_id)
            .where(UsersPositionModel.user_id == dto.user_id)
        )
        result = await self._session.execute(stmt)
        users_position = result.scalar_one_or_none()

        if not users_position:
            raise UsersPositionNotFound

        if dto.new_struct_adm_id:
            users_position.struct_adm_id = dto.new_struct_adm_id
        if dto.new_position_id:
            users_position.position_id = dto.new_position_id

        await self._session.flush()
        return users_position

    async def get_for_check(self, dto: GetUsersPositionDTO, company_id: UUID) -> UsersPositionDTO:
        stmt = (
            select(UsersPositionModel)
            .join(UsersReplicaModel, UsersReplicaModel.id == UsersPositionModel.user_id)
            .join(PositionModel, PositionModel.id == UsersPositionModel.position_id)
            .join(StructAdmModel, StructAdmModel.id == UsersPositionModel.struct_adm_id)
            .where(
                UsersPositionModel.user_id == dto.user_id,
                UsersPositionModel.position_id == dto.position_id,
                UsersPositionModel.struct_adm_id == dto.struct_adm_id,
                UsersReplicaModel.company_id == company_id,
                PositionModel.company_id == company_id,
                StructAdmModel.company_id == company_id,
            )
        )

        result = await self._session.execute(stmt)
        users_position = result.scalar_one_or_none()

        if users_position is None:
            raise UsersPositionNotFound

        return self._to_domain(users_position)

    async def update_role(self, dto: UpdateRoleUsersPositionDTO) -> UsersPositionDTO:
        if dto.role == Role.MANAGER:
            stmt = (
                select(UsersPositionModel)
                .where(UsersPositionModel.struct_adm_id == dto.struct_adm_id)
                .where(UsersPositionModel.role == Role.MANAGER)
            )
            result = await self._session.execute(stmt)
            old_users_position = result.scalar_one_or_none()
            if old_users_position:
                old_users_position.role = Role.MEMBER

        stmt = (
            select(UsersPositionModel)
            .where(UsersPositionModel.struct_adm_id == dto.struct_adm_id)
            .where(UsersPositionModel.position_id == dto.position_id)
            .where(UsersPositionModel.user_id == dto.user_id)
        )
        result = await self._session.execute(stmt)
        users_position = result.scalar_one_or_none()
        users_position.role = dto.role
        await self._session.flush()
        return self._to_domain(users_position)

    async def get_manager(self, dto: GetManagerPositionDTO) -> UsersPositionDTO | None:
        stmt = (
            select(UsersPositionModel)
            .where(UsersPositionModel.struct_adm_id == dto.struct_adm_id)
            .where(UsersPositionModel.role == Role.MANAGER)
        )
        result = await self._session.execute(stmt)
        users_position = result.scalar_one_or_none()
        if users_position is None:
            return None
        return self._to_domain(users_position)

    @staticmethod
    def _to_domain(users_position: UsersPositionModel) -> UsersPositionDTO:
        return UsersPositionDTO(
            user_id=users_position.user_id,
            struct_adm_id=users_position.struct_adm_id,
            position_id=users_position.position_id,
            role=users_position.role,
        )
