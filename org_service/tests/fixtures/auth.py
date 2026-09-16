import uuid

import pytest
from api.v1.token_dependencies import get_current_token
from app import app
from domain.token.models import MemberRoles, MembershipAdmission, TokenDTO


@pytest.fixture()
def set_auth_token():
    def _set(company_id, role: MemberRoles = MemberRoles.ADMIN, user_id=None):
        token = TokenDTO(
            subject=user_id or uuid.uuid4(), memberships=[MembershipAdmission(company_id=company_id, role=role)]
        )

        async def override_get_current_token():
            return token

        app.dependency_overrides[get_current_token] = override_get_current_token

    return _set
