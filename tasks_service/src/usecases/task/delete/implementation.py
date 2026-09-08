# from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from uuid import UUID

from domain.task.exceptions import TaskNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractDeleteTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLDeleteTaskUseCase(AbstractDeleteTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, task_id: UUID) -> None:
        async with self._uow as uow:
            task = await uow.task.get(task_id=task_id)
            if not task or task.company_id != company_id:
                raise TaskNotFound
            await uow.task_watcher.delete_by_task(task_id=task_id)
            await uow.task_assignees.delete_by_task(task_id=task_id)

            await uow.task.delete(task_id=task_id)
