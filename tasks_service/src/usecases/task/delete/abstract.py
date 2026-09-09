from abc import ABC, abstractmethod
from uuid import UUID


class AbstractDeleteTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, company_id: UUID, task_id: UUID) -> None: ...
