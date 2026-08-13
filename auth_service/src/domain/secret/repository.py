from abc import ABC, abstractmethod
from uuid import UUID

from domain.secret.exceptions import SecretNotFound
from domain.abstract import AbstractRepository
from .models import SecretDTO, CreateSecretDTO


class AbstractSecretRepository(AbstractRepository[SecretDTO, UUID, CreateSecretDTO], ABC):
    @abstractmethod
    def check_and_get_by_account_id(self, account_id: UUID, password: str) -> SecretDTO:
        raise SecretNotFound

    @abstractmethod
    async def get_by_account_id(self, account_id) -> SecretDTO | None:
        raise SecretNotFound

    # @abstractmethod
    # async def find_by_filters(self, filters: FilterDTO) -> List[DTO]:
    #     raise NotFound