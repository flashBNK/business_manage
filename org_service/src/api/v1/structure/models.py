from uuid import UUID

from pydantic import BaseModel


class CreateStructAdmSchema(BaseModel):
    name: str


class MoveStructAdmSchema(BaseModel):
    new_parent_id: UUID


class StructAdmSchema(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    path: str
    manager_id: UUID | None = None
