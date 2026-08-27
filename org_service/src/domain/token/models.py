import enum
import uuid
from dataclasses import dataclass, field


class MemberRoles(enum.StrEnum):
    ADMIN = "admin"
    MEMBER = "member"
    OWNER = "owner"


@dataclass(slots=True)
class MembershipAdmission:
    company_id: uuid.UUID
    role: MemberRoles


@dataclass(slots=True)
class TokenDTO:
    subject: uuid.UUID
    memberships: list[MembershipAdmission] = field(default_factory=list)
