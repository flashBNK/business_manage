from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import UsersReplicaNotFound
from .models import CreateUsersReplicaDTO, UsersReplicaDTO


class AbstractUsersReplicaRepository(AbstractRepository[UsersReplicaDTO, UUID, CreateUsersReplicaDTO], ABC):
    @abstractmethod
    async def upsert(self, dto: CreateUsersReplicaDTO) -> UsersReplicaDTO:
        raise UsersReplicaNotFound
