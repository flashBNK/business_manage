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