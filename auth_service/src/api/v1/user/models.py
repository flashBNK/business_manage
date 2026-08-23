import uuid
from datetime import datetime

from infrastructure.databases.postgresql.models.user import UserStatus
from pydantic import BaseModel, EmailStr


class CheckAccountSchema(BaseModel):
    email: EmailStr


class UserSchema(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    status: UserStatus
    created_at: datetime


class UpdateUserSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
