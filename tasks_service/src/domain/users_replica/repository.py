from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import UsersReplicaNotFound
from .models import CreateUsersReplicaDTO, UsersReplicaDTO


class AbstractUsersReplicaRepository(AbstractRepository[UsersReplicaDTO, UUID, CreateUsersReplicaDTO], ABC):
    @abstractmethod
    async def upsert(self, dto: CreateUsersReplicaDTO) -> UsersReplicaDTO:
        raise UsersReplicaNotFound

    @abstractmethod
    async def deactivate(self, users_replica_id: UUID, company_id: UUID, last_event_at: datetime) -> None:
        ...
