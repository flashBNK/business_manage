import uuid
from dataclasses import dataclass
from datetime import datetime

from infrastructure.databases.postgresql.models.user import UserStatus


@dataclass(slots=True)
class UserDTO:
    id: uuid.UUID
    first_name: str
    last_name: str
    status: UserStatus
    created_at: datetime


@dataclass(slots=True)
class CreateUserDTO:
    first_name: str
    last_name: str


@dataclass(slots=True)
class UpdateUserDTO:
    first_name: str | None = None
    last_name: str | None = None