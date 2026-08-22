import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from domain.token.models import MembershipAdmission


class CreateAccountSchema(BaseModel):
    email: EmailStr

class AccountSchema(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    verified_at: datetime

class ListAccountsSchema(BaseModel):
    total: int
    accounts: list[AccountSchema]

class RequestEmailChangeSchema(BaseModel):
    new_email: EmailStr

class ConfirmSchema(BaseModel):
    invite_code: str

class ConfirmAccountSchema(BaseModel):
    email: EmailStr
    code: str


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    subject: uuid.UUID
    memberships: list[MembershipAdmission]


class LoginResultSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshSchema(BaseModel):
    refresh_token: str


class CompleteSingUpSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    email: EmailStr
    password: str = Field(alias="password")
    first_name: str
    last_name: str
    company_name: str | None