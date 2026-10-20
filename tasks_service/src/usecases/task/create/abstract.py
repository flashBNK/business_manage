from abc import ABC, abstractmethod

from domain.idempotency.models import SavedResponseDTO
from domain.task.models import CreateTaskDTO


class AbstractCreateTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateTaskDTO, idempotency_key: str | None = None) -> SavedResponseDTO: ...
