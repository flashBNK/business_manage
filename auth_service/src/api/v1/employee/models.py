import uuid
from pydantic import BaseModel, EmailStr

from infrastructure.databases.postgresql.models.members import MemberRoles

class CreateEmployeeSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: MemberRoles


class CreateEmployeeResultSchema(BaseModel):
    user_id: uuid.UUID
    member_id: uuid.UUID



class CompleteEmployeeInviteSchema(BaseModel):
    invite_token: str
    password: str