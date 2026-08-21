import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AccountDTO:
    id: uuid.UUID
    email: str
    is_verified: bool
    verified_at: datetime


@dataclass(slots=True)
class CreateAccountDTO:
    email: str

@dataclass(slots=True)
class ConfirmAccountDTO:
    email: str
    code: str

@dataclass(slots=True)
class CompleteSignUpDTO:
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: str

@dataclass(slots=True)
class RequestEmailChangeDTO:
    user_id: uuid.UUID
    new_email: str

@dataclass(slots=True)
class ConfirmEmailChangeDTO:
    user_id: uuid.UUID
    account_id: uuid.UUID
    invite_code: str

@dataclass(slots=True)
class UpdateAccountDTO:
    email: str