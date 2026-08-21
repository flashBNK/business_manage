import uuid
from dataclasses import dataclass
from datetime import datetime

from infrastructure.databases.postgresql.models.invite import InviteStatus


@dataclass(slots=True)
class InviteDTO:
    id: uuid.UUID
    email: str
    code: str
    attempts: int
    expires_at: datetime | None
    status: InviteStatus
    accepted_at: datetime | None
    user_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None


@dataclass(slots=True)
class CreateInviteDTO:
    email: str
    code: str
    user_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    expires_at: datetime | None = None

@dataclass(slots=True)
class UpdateInviteDTO:
    attempts: int | None = None
    status: InviteStatus | None = None

@dataclass(slots=True)
class CompleteEmployeeInviteDTO:
    invite_token: str
    password: str