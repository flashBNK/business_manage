from abc import ABC, abstractmethod
from uuid import UUID


class AbstractDeletePositionUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, position_id: UUID) -> None: ...
