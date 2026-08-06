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


@dataclass(slots=True)
class CreateInviteDTO:
    email: str
    code: str
    expires_at: datetime | None = None

@dataclass(slots=True)
class UpdateInviteDTO:
    attempts: int
    email: str