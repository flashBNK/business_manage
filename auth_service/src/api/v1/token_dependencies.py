from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from container import Container
from domain.token.exceptions import InvalidToken, TokenExpired
from domain.token.models import TokenDTO

bearer_scheme = HTTPBearer()


def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token_service = Container.token_service()

    try:
        return token_service.decode_access_token(credentials.credentials)
    except InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except TokenExpired:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
