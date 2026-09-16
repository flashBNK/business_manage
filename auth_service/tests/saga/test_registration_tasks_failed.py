from uuid import UUID

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.databases.postgresql.models.user import User
from infrastructure.kafka.consumer.handlers import (
    handle_employee_registered,
    handle_org_compensated,
    handle_org_completed,
    handle_tasks_failed,
)
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy import select

from .conftest import create_employee, get_root_structure, make_event, publish_outbox_event


@pytest.mark.asyncio
async def test_registration_saga_tasks_failure(client, session, admin, org_client, kafka):
    company_id = admin["company_id"]
    headers = {"Authorization": f"Bearer {admin['access_token']}"}

    await publish_outbox_event(session, kafka, "company.created", company_id)

    root_id = await get_root_structure(org_client, company_id, admin["access_token"])

    response = await org_client.post(
        f"/api/v1/companies/{company_id}/positions", json={"name": f"Backend {company_id}"}, headers=headers
    )
    assert response.status_code == 201

    position_id = UUID(response.json()["id"])
    response = await org_client.post(
        f"/api/v1/companies/{company_id}/structure/{root_id}/positions/{position_id}", headers=headers
    )
    assert response.status_code == 201

    employee = await create_employee(client, session, admin, root_id, position_id)

    await publish_outbox_event(session, kafka, "employee.created", employee["user_id"])

    response = await client.post(
        "/api/v1/employees/invite-complete",
        json={"invite_token": employee["invite"].code, "password": employee["password"]},
    )

    assert response.status_code == 201

    employee_registered = await publish_outbox_event(session, kafka, "employee.registered", employee["user_id"])

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_employee_registered(
            event=EventEnvelopeDTO.from_dict(
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
            ),
            uow=uow,
        )

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))
    assert saga is not None

    org_provision = await publish_outbox_event(session, kafka, "registration.org.provision", saga.id)
    org_completed = await kafka.wait_for_event("registration.org.completed", org_provision.correlation_id)

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_org_completed(event=EventEnvelopeDTO.from_dict(org_completed), uow=uow)

    tasks_failed = make_event(
        event_type="registration.tasks.failed",
        aggregate_id=saga.id,
        correlation_id=saga.correlation_id,
        payload={
            "saga_id": str(saga.id),
            "user_id": str(employee["user_id"]),
            "company_id": str(company_id),
            "invite_id": str(employee["invite"].id),
            "struct_adm_id": str(root_id),
            "position_id": str(position_id),
            "reason": "test failure",
        },
    )

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_tasks_failed(event=EventEnvelopeDTO.from_dict(tasks_failed), uow=uow)

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))

    assert saga is not None
    assert saga.status == RegistrationStatus.COMPENSATING

    compensate = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "registration.org.compensate", OutboxEvent.aggregate_id == saga.id
        )
    )
    assert compensate is not None

    await publish_outbox_event(session, kafka, "registration.org.compensate", saga.id)

    org_compensated = await kafka.wait_for_event("registration.org.compensated", compensate.correlation_id)

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_org_compensated(event=EventEnvelopeDTO.from_dict(org_compensated), uow=uow)

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))

    assert saga is not None
    assert saga.status == RegistrationStatus.FAILED

    registration_failed = await session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_type == "registration.failed", OutboxEvent.aggregate_id == saga.id)
    )
    assert registration_failed is not None

    user = await session.scalar(select(User).where(User.id == employee["user_id"]))
    assert user is None

    response = await org_client.get(f"/api/v1/companies/{company_id}/structure/{root_id}/employees", headers=headers)
    assert response.status_code == 200

    employees = response.json()["employees"]
    assert response.json()["total"] == 0
    assert not employees
