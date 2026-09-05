from uuid import UUID

from pydantic import BaseModel, Field


class CreateStructAdmSchema(BaseModel):
    name: str


class MoveStructAdmSchema(BaseModel):
    new_parent_id: UUID


class StructAdmSchema(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    path: str


class StructAdmTreeSchema(BaseModel):
    id: UUID
    name: str
    children: list["StructAdmTreeSchema"] = Field(default_factory=list)


class CompanyStructureSchema(BaseModel):
    id: UUID
    name: str
    children: list[StructAdmTreeSchema] = Field(default_factory=list)
