# from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from uuid import UUID

from domain.task.exceptions import TaskNotFound
from domain.task.models import UpdateTaskDTO, ResponseTaskDTO
from domain.task.participants import check_participant
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractUpdateTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLUpdateTaskUseCase(AbstractUpdateTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: UpdateTaskDTO, company_id: UUID, task_id: UUID) -> ResponseTaskDTO:
        async with self._uow as uow:
            task = await uow.task.get(task_id=task_id)
            if not task or task.company_id != company_id:
                raise TaskNotFound

            if dto.responsible_id and dto.responsible_id != task.responsible_id:
                await check_participant(user_id=dto.responsible_id, company_id=company_id, uow=uow)

            if dto.watcher_ids:
                for user_id in {*dto.watcher_ids}:
                    await check_participant(user_id=user_id, company_id=company_id, uow=uow)

            if dto.assignee_ids:
                for user_id in {*dto.assignee_ids}:
                    await check_participant(user_id=user_id, company_id=company_id, uow=uow)

            task = await uow.task.update(dto=dto, task_id=task_id)

            if dto.watcher_ids is not None:
                old_watchers = await uow.task_watcher.list_by_task(task_id=task.id)
                old_watcher_ids = set(watcher.user_id for watcher in old_watchers)
                new_watcher_ids = set(dto.watcher_ids)
                remove_watcher_ids = old_watcher_ids - new_watcher_ids
                create_watcher_ids = new_watcher_ids - (old_watcher_ids - remove_watcher_ids)

                if remove_watcher_ids:
                    await uow.task_watcher.delete_by_list(watcher_ids=list(remove_watcher_ids))

                if create_watcher_ids:
                    await uow.task_watcher.create_many(
                        watcher_ids=list(create_watcher_ids), task_id=task.id
                    )

            if dto.assignee_ids is not None:
                old_assignees = await uow.task_assignees.list_by_task(task_id=task.id)
                old_assignee_ids = set(assignee.user_id for assignee in old_assignees)
                new_assignee_ids = set(dto.assignee_ids)
                remove_assignee_ids = old_assignee_ids - new_assignee_ids
                create_assignee_ids = new_assignee_ids - (old_assignee_ids - remove_assignee_ids)

                if remove_assignee_ids:
                    await uow.task_assignees.delete_by_list(assignee_ids=list(remove_assignee_ids))

                if create_assignee_ids:
                    await uow.task_assignees.create_many(
                        assignee_ids=list(create_assignee_ids), task_id=task.id
                    )

            assignees = await uow.task_assignees.list_by_task(task_id=task.id)
            watchers = await uow.task_watcher.list_by_task(task_id=task.id)
            response = ResponseTaskDTO(
                task=task,
                assignee_ids=[assignee.user_id for assignee in assignees] if assignees else [],
                watcher_ids=[watcher.user_id for watcher in watchers] if watchers else [],
            )

            return response
