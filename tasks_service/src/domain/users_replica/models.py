from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class UsersReplicaDTO:
    id: UUID
    username: str
    company_id: UUID | None
    last_event_at: datetime
    is_active: bool = False


@dataclass(slots=True)
class CreateUsersReplicaDTO(UsersReplicaDTO):
    pass
