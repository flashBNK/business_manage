from uuid import UUID

from infrastructure.databases.postgresql.models.users_position import Role
from pydantic import BaseModel


class CreateUsersPositionSchema(BaseModel):
    user_id: UUID
    position_id: UUID
    role: Role


class UsersPositionSchema(CreateUsersPositionSchema):
    struct_adm_id: UUID


class UsersReplicaSchema(BaseModel):
    id: UUID
    username: str
    is_active: bool
    company_id: UUID


class EmployeePositionSchema(BaseModel):
    user_id: UUID
    username: str
    position_id: UUID
    position_name: str
    role: Role


class UpdateUsersPositionSchema(BaseModel):
    struct_adm_id: UUID
    position_id: UUID
    role: Role
