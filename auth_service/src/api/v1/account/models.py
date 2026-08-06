from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CreateAccountSchema(BaseModel):
    email: EmailStr

class AccountSchema(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    verified_at: datetime

class ConfirmAccountSchema(BaseModel):
    email: EmailStr
    code: str