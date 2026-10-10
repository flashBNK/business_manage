import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from domain.abstract import AbstractRepository

from .exceptions import RegistrationSagaNotFound
from .models import CreateRegistrationSagaDTO, RegistrationSagaDTO


class AbstractRegistrationSagaRepository(
    AbstractRepository[RegistrationSagaDTO, uuid.UUID, CreateRegistrationSagaDTO],
    ABC,
):
    @abstractmethod
    async def get_by_correlation_id(self, correlation_id: uuid.UUID) -> RegistrationSagaDTO | None:
        raise RegistrationSagaNotFound

    @abstractmethod
    async def update_status(self, saga_id: uuid.UUID, status, deadline_at: datetime | None) -> RegistrationSagaDTO:
        raise RegistrationSagaNotFound

    async def get_expired(self, now: datetime) -> list[RegistrationSagaDTO]:
        raise RegistrationSagaNotFound

    async def mark_timeout(self, saga_id: uuid.UUID, last_error: str) -> None:
        raise RegistrationSagaNotFound
