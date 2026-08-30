from abc import ABC, abstractmethod
from uuid import UUID


class AbstractDeleteStructAdmUseCase(ABC):
    @abstractmethod
    async def execute(self, struct_adm_id: UUID, company_id: UUID) -> None: ...
