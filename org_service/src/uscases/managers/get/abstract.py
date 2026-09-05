from abc import ABC, abstractmethod

from domain.struct_adm.models import ManagerDTO
from domain.users_position.models import GetManagerDTO


class AbstractGetManagerStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: GetManagerDTO) -> ManagerDTO: ...
