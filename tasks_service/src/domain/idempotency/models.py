from dataclasses import dataclass

from domain.task.models import ResponseTaskDTO


@dataclass(slots=True)
class SavedResponseDTO:
    status_code: int
    body: ResponseTaskDTO


@dataclass(slots=True)
class IdempotencyRequestDTO:
    request_hash: str
    response_status: int | None = None
    response_body: dict | None = None
