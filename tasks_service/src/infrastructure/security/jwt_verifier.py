import uuid

import jwt
from domain.token.exceptions import InvalidToken, TokenExpired
from domain.token.models import MembershipAdmission, TokenDTO


class JVTTokenVerifier:
    def __init__(self, public_key: str, algorithm: str):
        self._public_key = public_key
        self._algorithm = algorithm

    def decode_access_token(self, token: str) -> TokenDTO:
        try:
            claims = jwt.decode(token, self._public_key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpired from exc
        except jwt.InvalidTokenError as exc:
            raise InvalidToken from exc

        return TokenDTO(
            subject=uuid.UUID(claims["subject"]),
            memberships=[
                MembershipAdmission(company_id=uuid.UUID(m["company_id"]), role=m["role"])
                for m in claims.get("memberships", [])
            ],
        )
