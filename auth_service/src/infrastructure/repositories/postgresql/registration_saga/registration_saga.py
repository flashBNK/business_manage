import uuid

from domain.registration_saga.exceptions import RegistrationSagaNotFound
from domain.registration_saga.models import CreateRegistrationSagaDTO, RegistrationSagaDTO
from domain.registration_saga.repository import AbstractRegistrationSagaRepository
from infrastructure.databases.postgresql.models.registration_saga import (
    RegistrationSaga as RegistrationSagaModel,
)
from infrastructure.databases.postgresql.models.registration_saga import (
    RegistrationStatus,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLRegistrationSagaRepository(AbstractRegistrationSagaRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateRegistrationSagaDTO) -> RegistrationSagaDTO:
        db_saga = RegistrationSagaModel(
            user_id=dto.user_id,
            company_id=dto.company_id,
            invite_id=dto.invite_id,
            correlation_id=dto.correlation_id,
            status=RegistrationStatus.STARTED,
        )

        self._session.add(db_saga)
        await self._session.flush()

        return self._to_domain(db_saga)

    async def get(self, saga_id: uuid.UUID) -> RegistrationSagaDTO | None:
        stmt = select(RegistrationSagaModel).where(RegistrationSagaModel.id == saga_id)
        result = await self._session.execute(stmt)
        saga = result.scalar_one_or_none()

        if saga is None:
            return None

        return self._to_domain(saga)

    async def get_by_correlation_id(self, correlation_id: uuid.UUID) -> RegistrationSagaDTO | None:
        stmt = select(RegistrationSagaModel).where(RegistrationSagaModel.correlation_id == correlation_id)
        result = await self._session.execute(stmt)
        saga = result.scalar_one_or_none()

        if saga is None:
            return None

        return self._to_domain(saga)

    async def update_status(self, saga_id: uuid.UUID, status: RegistrationStatus) -> RegistrationSagaDTO:
        stmt = select(RegistrationSagaModel).where(RegistrationSagaModel.id == saga_id)
        result = await self._session.execute(stmt)
        saga = result.scalar_one_or_none()

        if saga is None:
            raise RegistrationSagaNotFound

        saga.status = status

        await self._session.flush()
        return self._to_domain(saga)

    async def delete(self, saga_id: uuid.UUID) -> None:
        stmt = select(RegistrationSagaModel).where(RegistrationSagaModel.id == saga_id)
        result = await self._session.execute(stmt)
        saga = result.scalar_one_or_none()

        if saga is None:
            return

        await self._session.delete(saga)
        await self._session.flush()

    @staticmethod
    def _to_domain(saga: RegistrationSagaModel) -> RegistrationSagaDTO:
        return RegistrationSagaDTO(
            id=saga.id,
            user_id=saga.user_id,
            company_id=saga.company_id,
            invite_id=saga.invite_id,
            correlation_id=saga.correlation_id,
            status=saga.status,
            created_at=saga.created_at,
            updated_at=saga.updated_at,
        )
