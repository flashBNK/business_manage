import uuid

from api.v1.token_dependencies import get_current_token
from domain.token.authorization import has_role_at_least, is_role_any
from domain.token.models import TokenDTO
from fastapi import Depends, HTTPException, status
from infrastructure.databases.postgresql.models.members import MemberRoles


def require_company_role(min_role: MemberRoles):
    def dependency(company_id: uuid.UUID, token: TokenDTO = Depends(get_current_token)) -> TokenDTO:
        if not has_role_at_least(company_id=company_id, token=token, min_role=min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to the requested resource is denied.",
            )
        return token

    return dependency


def require_role_any(min_role: MemberRoles):
    def dependency(token: TokenDTO = Depends(get_current_token)) -> TokenDTO:
        if not is_role_any(min_role=min_role, token=token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to the requested resource is denied.",
            )
        return token

    return dependency
