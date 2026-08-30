from uuid import UUID

from pydantic import BaseModel


class CreatePositionSchema(BaseModel):
    name: str
    description: str | None = None


class UpdatePositionSchema(BaseModel):
    name: str | None = None
    description: str | None = None


class PositionSchema(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: str | None = None
