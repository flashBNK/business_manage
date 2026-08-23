import uuid

from domain.token.models import MembershipAdmission, TokenDTO
from infrastructure.databases.postgresql.models.members import MemberRoles

ROLE_RANK: dict[MemberRoles, int] = {
    MemberRoles.MEMBER: 0,
    MemberRoles.ADMIN: 1,
}


def get_membership(token: TokenDTO, company_id: uuid.UUID) -> MembershipAdmission:
    return next(
        (membership for membership in token.memberships if membership.company_id == company_id),
        None,
    )


def has_role_at_least(token: TokenDTO, company_id: uuid.UUID, min_role: MemberRoles) -> bool:
    membership = get_membership(token, company_id)
    if not membership:
        return False
    return ROLE_RANK[membership.role] >= ROLE_RANK[min_role]


def is_role_any(token: TokenDTO, min_role: MemberRoles) -> bool:
    return any(ROLE_RANK[membership.role] >= ROLE_RANK[min_role] for membership in token.memberships)
