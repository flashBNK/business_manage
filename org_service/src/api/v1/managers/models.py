from uuid import UUID

from infrastructure.databases.postgresql.models.users_position import Role
from pydantic import BaseModel


class AddManagerStructAdmSchema(BaseModel):
    user_id: UUID
    position_id: UUID


class DeleteManagerStructAdmSchema(AddManagerStructAdmSchema):
    pass


class ManagerSchema(AddManagerStructAdmSchema):
    struct_adm_id: UUID
    role: Role
