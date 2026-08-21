from abc import ABC, abstractmethod

from domain.invite.models import CompleteEmployeeInviteDTO
from domain.token.models import LoginResultDTO


class AbstractCompleteEmployeeInviteUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CompleteEmployeeInviteDTO) -> LoginResultDTO:
        ...