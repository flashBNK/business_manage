from uuid import UUID, uuid4

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.exceptions import InvalidTaskStatusTransition, TaskNotFound
from domain.task.models import STATUS_TRANSITIONS, ChangeStatusTaskDTO, ResponseTaskDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

from .abstract import AbstractChangeStatusTaskUseCase

log = get_logger(__name__)


class PostgreSQLChangeStatusTaskUseCase(AbstractChangeStatusTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: ChangeStatusTaskDTO, company_id: UUID, task_id: UUID) -> ResponseTaskDTO:
        correlation_id = uuid4()
        async with self._uow as uow:
            task = await uow.task.get_for_update(task_id=task_id, company_id=company_id)
            if task is None:
                raise TaskNotFound

            old_status = task.status

            if old_status != dto.status:
                if dto.status not in STATUS_TRANSITIONS[old_status]:
                    raise InvalidTaskStatusTransition

                task = await uow.task.change_status(dto=dto, task_id=task_id)

            assignees = await uow.task_assignees.list_by_task(task_id=task.id)
            watchers = await uow.task_watcher.list_by_task(task_id=task.id)

            response = ResponseTaskDTO(
                task=task,
                assignee_ids=[a.user_id for a in assignees],
                watcher_ids=[w.user_id for w in watchers],
            )

            if old_status != task.status:
                await uow.outbox_event.create(
                    CreateOutboxEventDTO(
                        event_type=OutboxEventType.TASK_STATUS_CHANGED,
                        aggregate_id=task.id,
                        correlation_id=correlation_id,
                        payload={
                            "old_status": old_status,
                            "new_status": task.status,
                        },
                    )
                )

            return response
