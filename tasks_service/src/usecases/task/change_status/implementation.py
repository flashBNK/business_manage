# from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from uuid import UUID

from domain.task.exceptions import TaskNotFound
from domain.task.models import UpdateTaskDTO, ResponseTaskDTO, ChangeStatusTaskDTO
from domain.task.participants import check_participant
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractChangeStatusTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLChangeStatusTaskUseCase(AbstractChangeStatusTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: ChangeStatusTaskDTO, company_id: UUID, task_id: UUID) -> ResponseTaskDTO:
        async with self._uow as uow:
            task = await uow.task.get(task_id=task_id)
            if not task or task.company_id != company_id:
                raise TaskNotFound

            task = await uow.task.change_status(dto=dto, task_id=task_id)

            assignees = await uow.task_assignees.list_by_task(task_id=task.id)
            watchers = await uow.task_watcher.list_by_task(task_id=task.id)

            response = ResponseTaskDTO(
                task=task,
                assignee_ids=[a.user_id for a in assignees],
                watcher_ids=[w.user_id for w in watchers],
            )

            return response
