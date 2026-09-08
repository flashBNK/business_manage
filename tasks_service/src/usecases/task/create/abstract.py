from abc import ABC, abstractmethod

from domain.task.models import CreateTaskDTO, TaskDTO


class AbstractCreateTaskUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateTaskDTO) -> TaskDTO: ...
