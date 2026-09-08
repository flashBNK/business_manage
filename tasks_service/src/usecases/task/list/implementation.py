from uuid import UUID

from domain.task.models import ResponseTaskDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractListTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLListTaskUseCase(AbstractListTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID) -> list[ResponseTaskDTO]:
        async with self._uow as uow:
            tasks = await uow.task.list_by_company(company_id=company_id)
            if not tasks:
                return []
            total = []
            for task in tasks:
                response = ResponseTaskDTO(
                    task=task,
                    watcher_ids=[watcher.user_id for watcher in await uow.task_watcher.list_by_task(task_id=task.id)],
                    assignee_ids=[assignee.user_id for assignee in await uow.task_assignees.list_by_task(task_id=task.id)]
                )
                total.append(response)

            return total
