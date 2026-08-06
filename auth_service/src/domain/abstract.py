from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")
TCreateDTO = TypeVar("TCreateDTO")
TUpdateDTO = TypeVar("TUpdateDTO")

class AbstractRepository(ABC, Generic[TEntity, TId, TCreateDTO]):
    @abstractmethod
    async def get(self, entity_id: TId) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def create(self, dto: TCreateDTO) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity_id: TId) -> None:
        raise NotImplementedError