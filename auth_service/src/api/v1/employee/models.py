import uuid
from datetime import datetime

from infrastructure.databases.postgresql.models.members import MemberRoles
from pydantic import BaseModel, EmailStr

from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus


class CreateEmployeeSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: MemberRoles
    struct_adm_id: uuid.UUID
    position_id: uuid.UUID


class CreateEmployeeResultSchema(BaseModel):
    user_id: uuid.UUID
    member_id: uuid.UUID


class CompleteEmployeeInviteSchema(BaseModel):
    invite_token: str
    password: str


class OnboardingStatusSchema(BaseModel):
    saga_id: uuid.UUID
    company_id: uuid.UUID
    status: RegistrationStatus
    correlation_id: uuid.UUID
    deadline_at: datetime | None
    last_error: str | None
    updated_at: datetime
