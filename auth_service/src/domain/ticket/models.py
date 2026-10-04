import uuid
from dataclasses import dataclass
from datetime import datetime

from infrastructure.databases.postgresql.models.invite import InviteStatus


@dataclass(slots=True)
class TicketDTO:
    id: uuid.UUID
    email: str
    code: str
    attempts: int
    expires_at: datetime | None
    created_at: datetime | None

@dataclass(slots=True)
class CreateTicketDTO:
    email: str
    code: str
    expires_at: datetime | None = None

