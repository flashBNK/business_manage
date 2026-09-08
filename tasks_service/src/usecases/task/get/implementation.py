from uuid import UUID

from domain.task.exceptions import TaskNotFound
from domain.task.models import  ResponseTaskDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractGetTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLGetTaskUseCase(AbstractGetTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, task_id: UUID) -> ResponseTaskDTO:
        async with self._uow as uow:
            task = await uow.task.get(task_id=task_id)
            if not task or task.company_id != company_id:
                raise TaskNotFound

            watchers_ids = [watcher.user_id for watcher in await uow.task_watcher.list_by_task(task_id=task_id)]
            assignees_ids = [assignee.user_id for assignee in await uow.task_assignees.list_by_task(task_id=task_id)]

            return ResponseTaskDTO(task=task, watcher_ids=watchers_ids, assignee_ids=assignees_ids)
