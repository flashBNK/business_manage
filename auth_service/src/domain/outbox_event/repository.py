from abc import ABC
from uuid import UUID

from domain.abstract import AbstractRepository

from .models import CreateOutboxEventDTO, OutboxEventDTO


class AbstractOutboxEventRepository(AbstractRepository[OutboxEventDTO, UUID, CreateOutboxEventDTO], ABC):
    pass
