import uuid

from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.models import CreateTaskDTO, TaskDTO
from domain.task.participants import validate_participant
from domain.task_assignees.models import CreateTaskAssigneesDTO
from domain.task_watchers.models import CreateTaskWatcherDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

from .abstract import AbstractCreateTaskUseCase

log = get_logger(__name__)


class PostgreSQLCreateTaskUseCase(AbstractCreateTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        correlation_id = uuid.uuid4()
        async with self._uow as uow:
            await validate_participant(
                author_id=dto.author_id,
                responsible_id=dto.responsible_id,
                company_id=dto.company_id,
                watcher_ids=dto.watcher_ids,
                assignee_ids=dto.assignee_ids,
                uow=uow,
            )

            task = await uow.task.create(dto=dto)

            for task_watcher_id in {*dto.watcher_ids}:
                log.info("Создание связанного task_watcher", task_watcher_id=task_watcher_id)
                await uow.task_watcher.create(dto=CreateTaskWatcherDTO(task_id=task.id, user_id=task_watcher_id))

            for task_assignee_id in {*dto.assignee_ids}:
                log.info("Создание связанного task_assignee", task_assignee_id=task_assignee_id)
                await uow.task_assignees.create(dto=CreateTaskAssigneesDTO(task_id=task.id, user_id=task_assignee_id))

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.TASK_CREATED,
                    aggregate_id=task.id,
                    correlation_id=correlation_id,
                    payload={
                        "title": task.title,
                        "description": task.description,
                        "author_id": str(task.author_id),
                        "responsible_id": str(task.responsible_id),
                        "company_id": str(task.company_id),
                        "deadline": task.deadline.isoformat() if task.deadline else None,
                        "status": task.status,
                        "estimated_minutes": task.estimated_minutes,
                        "assignee_ids": [str(assignee_id) for assignee_id in dto.assignee_ids],
                        "watcher_ids": [str(watcher_id) for watcher_id in dto.watcher_ids],
                    },
                )
            )

            return task
