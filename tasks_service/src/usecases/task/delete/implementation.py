from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.exceptions import TaskNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

from .abstract import AbstractDeleteTaskUseCase

log = get_logger(__name__)


class PostgreSQLDeleteTaskUseCase(AbstractDeleteTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, task_id: UUID) -> None:
        correlation_id = uuid4()
        async with self._uow as uow:
            task = await uow.task.get(task_id=task_id)
            if not task or task.company_id != company_id:
                raise TaskNotFound
            await uow.task_watcher.delete_by_task(task_id=task_id)
            await uow.task_assignees.delete_by_task(task_id=task_id)

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.TASK_DELETED,
                    aggregate_id=task.id,
                    correlation_id=correlation_id,
                    payload={},
                )
            )

            await uow.task.delete(task_id=task_id)
