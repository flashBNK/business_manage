import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository
from domain.secret.exceptions import SecretNotFound

from .models import CreateSecretDTO, SecretDTO


class AbstractSecretRepository(AbstractRepository[SecretDTO, UUID, CreateSecretDTO], ABC):
    @abstractmethod
    def check_and_get_by_account_id(self, account_id: UUID, password: str) -> SecretDTO:
        raise SecretNotFound

    @abstractmethod
    async def get_by_account_id(self, account_id) -> SecretDTO | None:
        raise SecretNotFound

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[SecretDTO]:
        raise SecretNotFound
