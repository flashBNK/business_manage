from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from infrastructure.databases.postgresql.models.company import Company
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from usecases.registration.recover.implementation import PostgreSQLRecoverRegistrationSagasUseCase


@pytest.mark.asyncio
async def test_tasks_step_times_out(session):
    now = datetime.now(UTC)
    company = Company(name="Test company")
    session.add(company)
    await session.flush()

    saga = RegistrationSaga(
        user_id=uuid4(),
        company_id=company.id,
        invite_id=uuid4(),
        correlation_id=uuid4(),
        status=RegistrationStatus.ORG_COMPLETED,
        deadline_at=now - timedelta(seconds=1),
    )
    session.add(saga)
    await session.commit()
    saga_id = saga.id

    for _ in range(2):
        usecase = PostgreSQLRecoverRegistrationSagasUseCase(uow=PostgreSQLAuthUnitOfWork(session=session))
        await usecase.execute(now=now)

    saga = await session.get(RegistrationSaga, saga_id)
    assert saga is not None
    assert saga.status == RegistrationStatus.TIMED_OUT
    assert saga.last_error == "tasks step timed out"
    assert saga.deadline_at is None
