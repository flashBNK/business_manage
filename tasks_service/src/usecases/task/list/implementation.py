from uuid import UUID

from domain.task.models import ListResponseTaskDTO, ResponseTaskDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

from .abstract import AbstractListTaskUseCase

log = get_logger(__name__)


class PostgreSQLListTaskUseCase(AbstractListTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, company_id: UUID, limit: int, offset: int) -> ListResponseTaskDTO:
        async with self._uow as uow:
            tasks, total = await uow.task.list_by_company(company_id=company_id, limit=limit, offset=offset)

            if not tasks:
                return ListResponseTaskDTO(total=total, tasks=[], limit=limit, offset=offset)

            task_ids = [task.id for task in tasks]

            watchers = await uow.task_watcher.list_by_tasks(task_ids=task_ids)
            assignees = await uow.task_assignees.list_by_tasks(task_ids=task_ids)

            watchers_by_task: dict[UUID, list[UUID]] = {task_id: [] for task_id in task_ids}
            assignees_by_task: dict[UUID, list[UUID]] = {task_id: [] for task_id in task_ids}

            for watcher in watchers:
                watchers_by_task[watcher.task_id].append(watcher.user_id)

            for assignee in assignees:
                assignees_by_task[assignee.task_id].append(assignee.user_id)

            responses = [
                ResponseTaskDTO(
                    task=task,
                    watcher_ids=watchers_by_task[task.id],
                    assignee_ids=assignees_by_task[task.id],
                )
                for task in tasks
            ]

            return ListResponseTaskDTO(
                total=total,
                tasks=responses,
                limit=limit,
                offset=offset,
            )
