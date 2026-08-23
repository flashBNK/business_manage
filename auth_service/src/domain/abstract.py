from abc import ABC, abstractmethod
from typing import TypeVar

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")
TCreateDTO = TypeVar("TCreateDTO")
TUpdateDTO = TypeVar("TUpdateDTO")


class AbstractRepository[TEntity, TId, TCreateDTO](ABC):
    @abstractmethod
    async def get(self, entity_id: TId) -> TEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, dto: TCreateDTO) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity_id: TId) -> None:
        raise NotImplementedError
