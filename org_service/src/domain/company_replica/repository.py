from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import CompanyReplicaNotFound
from .models import CompanyReplicaDTO, CreateCompanyReplicaDTO


class AbstractCompanyReplicaRepository(AbstractRepository[CompanyReplicaDTO, UUID, CreateCompanyReplicaDTO], ABC):
    @abstractmethod
    async def upsert(self, dto: CreateCompanyReplicaDTO) -> CompanyReplicaDTO:
        raise CompanyReplicaNotFound
