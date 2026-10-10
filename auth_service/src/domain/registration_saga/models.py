import uuid
from dataclasses import dataclass
from datetime import datetime

from infrastructure.databases.postgresql.models.registration_saga import RegistrationStatus


@dataclass(slots=True)
class RegistrationSagaDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    company_id: uuid.UUID
    invite_id: uuid.UUID
    correlation_id: uuid.UUID
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime
    deadline_at: datetime | None
    last_error: str | None


@dataclass(slots=True)
class CreateRegistrationSagaDTO:
    user_id: uuid.UUID
    company_id: uuid.UUID
    invite_id: uuid.UUID
    correlation_id: uuid.UUID
    deadline_at: datetime | None
