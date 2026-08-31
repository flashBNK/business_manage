from uuid import UUID

from pydantic import BaseModel


class CreateStructAdmPositionSchema(BaseModel):
    struct_adm_id: UUID
    position_id: UUID


class StructAdmPositionSchema(CreateStructAdmPositionSchema):
    pass
