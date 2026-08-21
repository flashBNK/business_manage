import uuid
from abc import ABC, abstractmethod

from domain.account.models import AccountDTO, RequestEmailChangeDTO, ConfirmEmailChangeDTO
from domain.user.models import UpdateUserDTO, UserDTO


class AbstractConfirmUpdateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: ConfirmEmailChangeDTO) -> AccountDTO:
        ...