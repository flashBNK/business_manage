import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RefreshTokenDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    expires_at: datetime
    revoked_at: datetime | None


@dataclass(slots=True)
class CreateRefreshTokenDTO:
    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
