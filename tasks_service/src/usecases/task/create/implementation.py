# from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.models import CreateTaskDTO, TaskDTO
from domain.task.participants import validate_participant
from domain.task_assignees.models import CreateTaskAssigneesDTO
from domain.task_watchers.models import CreateTaskWatcherDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork

from .abstract import AbstractCreateTaskUseCase
from logger import get_logger
log = get_logger(__name__)


class PostgreSQLCreateTaskUseCase(AbstractCreateTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        # correlation_id = uuid.uuid4()
        async with self._uow as uow:
            await validate_participant(
                author_id=dto.author_id,
                responsible_id=dto.responsible_id,
                company_id=dto.company_id,
                watcher_ids=dto.watcher_ids,
                assignee_ids=dto.assignee_ids,
                uow=uow
            )

            task = await uow.task.create(dto=dto)

            for task_watcher_id in {*dto.watcher_ids}:
                log.info("Попытка создания связанного task_watcher", task_watcher_id=task_watcher_id)
                await uow.task_watcher.create(dto=CreateTaskWatcherDTO(task_id=task.id, user_id=task_watcher_id))

            for task_assignee_id in {*dto.assignee_ids}:
                log.info("Попытка создания связанного task_assignee", task_assignee_id=task_assignee_id)
                await uow.task_assignees.create(dto=CreateTaskAssigneesDTO(task_id=task.id, user_id=task_assignee_id))

            # await uow.outbox_event.create(
            #     CreateOutboxEventDTO(
            #         event_type=OutboxEventType.POSITION_CREATED,
            #         aggregate_id=position.id,
            #         correlation_id=correlation_id,
            #         payload={
            #             "company_id": str(dto.company_id),
            #             "position_id": str(position.id),
            #             "name": str(position.name),
            #             "description": str(position.description),
            #         },
            #     )
            # )

            return task
