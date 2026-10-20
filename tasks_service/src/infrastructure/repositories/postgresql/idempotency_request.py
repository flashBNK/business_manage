from pydantic import TypeAdapter

from domain.idempotency.models import IdempotencyRequestDTO, SavedResponseDTO
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.databases.postgresql.models.idempotency_request import IdempotencyRequest as IdempotencyRequestModel

from domain.task.models import ResponseTaskDTO


class PostgreSQLIdempotencyRequestRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def reserve(self, scope: str, key: str, request_hash: str) -> bool:
        stmt = (
            insert(IdempotencyRequestModel)
            .values(scope=scope, key=key, request_hash=request_hash)
            .on_conflict_do_nothing(index_elements=["scope", "key"])
            .returning(IdempotencyRequestModel)
        )
        result = await self._session.execute(stmt)
        idempotency_request = result.scalar_one_or_none()
        return idempotency_request is not None

    async def get(self, scope: str, key: str) -> IdempotencyRequestDTO:
        stmt = select(IdempotencyRequestModel).where(IdempotencyRequestModel.scope == scope, IdempotencyRequestModel.key == key)
        result = await self._session.execute(stmt)
        idempotency_request = result.scalar_one_or_none()
        return IdempotencyRequestDTO(
            request_hash=idempotency_request.request_hash,
            response_status=idempotency_request.response_status,
            response_body=idempotency_request.response_body,
        )

    async def complete(self, scope: str, key: str, response: SavedResponseDTO) -> None:
        body_for_db = TypeAdapter(ResponseTaskDTO).dump_python(response.body, mode="json")

        stmt = (
            update(IdempotencyRequestModel)
            .where(IdempotencyRequestModel.scope == scope, IdempotencyRequestModel.key == key)
            .values(response_status=response.status_code, response_body=body_for_db)
        )
        await self._session.execute(stmt)
