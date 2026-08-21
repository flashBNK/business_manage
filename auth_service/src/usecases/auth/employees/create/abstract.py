from abc import ABC, abstractmethod

from domain.member.models import CreateEmployeeResultDTO, CreateEmployeeDTO


class AbstractCreateEmployeeUseCase(ABC):
    @abstractmethod
    async def execute(self, dto: CreateEmployeeDTO) -> CreateEmployeeResultDTO:
        ...