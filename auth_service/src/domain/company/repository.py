from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import CompanyNotFound
from .models import CompanyDTO, CreateCompanyDTO


class AbstractCompanyRepository(AbstractRepository[CompanyDTO, UUID, CreateCompanyDTO], ABC):
    @abstractmethod
    async def get_by_name(self, company_dto: CreateCompanyDTO) -> CompanyDTO | None:
        raise CompanyNotFound

    # @abstractmethod
    # async def find_by_filters(self, filters: FilterDTO) -> List[DTO]:
    #     raise NotFound
