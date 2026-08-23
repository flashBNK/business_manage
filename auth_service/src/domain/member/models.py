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


@dataclass(slots=True)
class CreateEmployeeDTO:
    email: str
    first_name: str
    last_name: str
    company_id: uuid.UUID
    role: MemberRoles = MemberRoles.MEMBER


@dataclass(slots=True)
class CreateEmployeeResultDTO:
    user_id: uuid.UUID
    member_id: uuid.UUID
