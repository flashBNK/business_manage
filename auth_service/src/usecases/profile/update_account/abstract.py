import uuid
from abc import ABC, abstractmethod

from domain.account.models import RequestEmailChangeDTO


class AbstractUpdateAccountUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: RequestEmailChangeDTO, account_id: uuid.UUID) -> None: ...
