from uuid import uuid4

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.databases.postgresql.models.user import User
from infrastructure.kafka.consumer.handlers import handle_employee_registered, handle_org_failed
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy import select

from .conftest import create_employee, get_root_structure, publish_outbox_event


@pytest.mark.asyncio
async def test_registration_saga_org_failure(client, session, admin, org_client, kafka):
    company_id = admin["company_id"]

    await publish_outbox_event(session, kafka, "company.created", company_id)

    root_id = await get_root_structure(org_client, company_id, admin["access_token"])

    invalid_position_id = uuid4()

    employee = await create_employee(client, session, admin, root_id, invalid_position_id)

    await publish_outbox_event(session, kafka, "employee.created", employee["user_id"])

    response = await client.post(
        "/api/v1/employees/invite-complete",
        json={"invite_token": employee["invite"].code, "password": employee["password"]},
    )
    assert response.status_code == 201

    employee_registered = await publish_outbox_event(session, kafka, "employee.registered", employee["user_id"])

    employee_registered_event = EventEnvelopeDTO.from_dict(
        {
            "event_id": str(employee_registered.event_id),
            "event_type": employee_registered.event_type,
            "schema_version": employee_registered.schema_version,
            "aggregate_id": str(employee_registered.aggregate_id),
            "correlation_id": str(employee_registered.correlation_id),
            "causation_id": None,
            "producer": employee_registered.producer,
            "occurred_at": employee_registered.occurred_at.isoformat(),
            "payload": employee_registered.payload,
        }
    )

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_employee_registered(event=employee_registered_event, uow=uow)

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))
    assert saga is not None

    org_provision = await publish_outbox_event(session, kafka, "registration.org.provision", saga.id)

    org_failed = await kafka.wait_for_event("registration.org.failed", org_provision.correlation_id)

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_org_failed(event=EventEnvelopeDTO.from_dict(org_failed), uow=uow)

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))
    assert saga is not None
    assert saga.status == RegistrationStatus.FAILED

    registration_failed = await session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_type == "registration.failed", OutboxEvent.aggregate_id == saga.id)
    )
    assert registration_failed is not None

    user = await session.scalar(select(User).where(User.id == employee["user_id"]))
    assert user is None
