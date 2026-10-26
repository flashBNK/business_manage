import hashlib
import json
import uuid

from domain.idempotency.exceptions import IdempotencyConflict
from domain.idempotency.models import SavedResponseDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.task.models import CreateTaskDTO, ResponseTaskDTO
from domain.task.participants import validate_participant
from domain.task_assignees.models import CreateTaskAssigneesDTO
from domain.task_watchers.models import CreateTaskWatcherDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger
from pydantic import TypeAdapter

from .abstract import AbstractCreateTaskUseCase

log = get_logger(__name__)


class PostgreSQLCreateTaskUseCase(AbstractCreateTaskUseCase):
    def __init__(self, uow: PostgreSQLTasksUnitOfWork):
        self._uow = uow

    async def execute(self, dto: CreateTaskDTO, idempotency_key: str | None = None) -> SavedResponseDTO:
        scope = f"task.create:{dto.company_id}:{dto.author_id}"
        request_body = TypeAdapter(CreateTaskDTO).dump_python(dto, mode="json")
        request_hash = hashlib.sha256(
            json.dumps(request_body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        correlation_id = uuid.uuid4()
        async with self._uow as uow:
            if idempotency_key is not None:
                reserved = await uow.idempotency_request.reserve(scope, idempotency_key, request_hash)
                if not reserved:
                    saved = await uow.idempotency_request.get(scope, idempotency_key)
                    if saved.request_hash != request_hash:
                        raise IdempotencyConflict
                    if saved.response_status is None or saved.response_body is None:
                        raise RuntimeError("Idempotency response is incomplete")
                    body = TypeAdapter(ResponseTaskDTO).validate_python(saved.response_body)
                    return SavedResponseDTO(status_code=saved.response_status, body=body)

            await validate_participant(
                author_id=dto.author_id,
                responsible_id=dto.responsible_id,
                company_id=dto.company_id,
                watcher_ids=dto.watcher_ids,
                assignee_ids=dto.assignee_ids,
                uow=uow,
            )

            task = await uow.task.create(dto=dto)

            for task_watcher_id in set(dto.watcher_ids):
                log.info("Создание связанного task_watcher", task_watcher_id=task_watcher_id)
                await uow.task_watcher.create(dto=CreateTaskWatcherDTO(task_id=task.id, user_id=task_watcher_id))

            for task_assignee_id in set(dto.assignee_ids):
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
                        "assignee_ids": request_body["assignee_ids"],
                        "watcher_ids": request_body["watcher_ids"],
                    },
                )
            )

            body = ResponseTaskDTO(task=task, watcher_ids=dto.watcher_ids, assignee_ids=dto.assignee_ids)
            response = SavedResponseDTO(status_code=201, body=body)
            TypeAdapter(ResponseTaskDTO).dump_python(response.body, mode="json")

            if idempotency_key is not None:
                await uow.idempotency_request.complete(scope, idempotency_key, response)

            return response
