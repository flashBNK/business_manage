import uuid
from dataclasses import dataclass

from infrastructure.databases.postgresql.models.members import MemberRoles


@dataclass(slots=True)
class MemberDTO:
    id: uuid.UUID
    user_id: uuid.UUID
    company_id: uuid.UUID
    invite_id: uuid.UUID
    role: MemberRoles
    is_active: bool


@dataclass(slots=True)
class CreateMemberDTO:
    user_id: uuid.UUID
    company_id: uuid.UUID
    role: MemberRoles
    invite_id: uuid.UUID | None = None