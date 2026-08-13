from abc import ABC, abstractmethod

from .exceptions import InvalidToken
from .models import TokenDTO


class AbstractTokenService(ABC):
    @abstractmethod
    def create_access_token(self, payload: TokenDTO) -> str:
        raise InvalidToken


    @abstractmethod
    def decode_access_token(self, token: str) -> TokenDTO:
        raise InvalidToken