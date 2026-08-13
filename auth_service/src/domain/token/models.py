import uuid

from dataclasses import dataclass, field

@dataclass(slots=True)
class MembershipAdmission:
    company_id: uuid.UUID
    role: str


@dataclass(slots=True)
class TokenDTO:
    subject: uuid.UUID
    memberships: list[MembershipAdmission] = field(default_factory=list)


@dataclass(slots=True)
class LoginResultDTO:
    access_token: str


@dataclass(slots=True)
class LoginDTO:
    email: str
    password: str