from dataclasses import dataclass
from uuid import UUID

from infrastructure.databases.postgresql.models.users_position import Role


@dataclass(slots=True)
class CreateUsersPositionDTO:
    user_id: UUID
    struct_adm_id: UUID
    position_id: UUID
    role: Role


@dataclass(slots=True)
class UsersPositionDTO(CreateUsersPositionDTO):
    pass


@dataclass(slots=True)
class GetUsersPositionDTO:
    user_id: UUID
    struct_adm_id: UUID
    position_id: UUID


@dataclass(slots=True)
class EmployeePositionDTO:
    user_id: UUID
    username: str
    position_id: UUID
    position_name: str
    role: Role


@dataclass(slots=True)
class UpdateUsersPositionDTO:
    user_id: UUID
    old_struct_adm_id: UUID
    old_position_id: UUID
    new_struct_adm_id: UUID | None
    new_position_id: UUID | None
    new_role: Role
