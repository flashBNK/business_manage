import uuid
import datetime
import jwt

from domain.token.exceptions import InvalidToken, TokenExpired
from domain.token.models import TokenDTO, MembershipAdmission
from domain.token.repository import AbstractTokenService

class JVTTokenService(AbstractTokenService):
    def __init__(self, private_key: str, public_key: str, algorithm: str, access_lifetime: int):
        self._private_key = private_key
        self._public_key = public_key
        self._algorithm = algorithm
        self._access_lifetime = datetime.timedelta(minutes=access_lifetime)

    def create_access_token(self, payload: TokenDTO) -> str:
        now = datetime.datetime.now(datetime.UTC)
        claims = {
            "subject": str(payload.subject),
            "memberships": [
                {"company_id": str(m.company_id), "role": m.role} for m in payload.memberships
            ],
            "iat": now,
            "exp": now + self._access_lifetime,
        }
        return jwt.encode(claims, self._private_key, algorithm=self._algorithm)

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