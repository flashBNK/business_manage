from abc import ABC, abstractmethod

from domain.member.models import CreateEmployeeDTO, CreateEmployeeResultDTO


class AbstractCreateEmployeeUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateEmployeeDTO) -> CreateEmployeeResultDTO: ...
