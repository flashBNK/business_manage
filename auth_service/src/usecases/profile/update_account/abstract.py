import uuid
from abc import ABC, abstractmethod

from domain.account.models import AccountDTO, RequestEmailChangeDTO
from domain.user.models import UpdateUserDTO, UserDTO


class AbstractUpdateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: RequestEmailChangeDTO, account_id: uuid.UUID) -> None:
        ...