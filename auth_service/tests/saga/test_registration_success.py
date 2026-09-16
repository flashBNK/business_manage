from uuid import UUID

import pytest
from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from infrastructure.databases.postgresql.models.registration_saga import RegistrationSaga, RegistrationStatus
from infrastructure.kafka.consumer.handlers import (
    handle_employee_registered,
    handle_org_completed,
    handle_registration_completed,
    handle_tasks_completed,
)
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy import select

from .conftest import create_employee, get_root_structure, publish_outbox_event


@pytest.mark.asyncio
async def test_registration_saga_success(client, session, admin, org_client, tasks_client, kafka):
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
    org_completed = await kafka.wait_for_event("registration.org.completed", org_provision.correlation_id)

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_org_completed(event=EventEnvelopeDTO.from_dict(org_completed), uow=uow)

    await publish_outbox_event(session, kafka, "registration.tasks.provision", saga.id)

    tasks_completed = await kafka.wait_for_event("registration.tasks.completed", UUID(org_completed["correlation_id"]))

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_tasks_completed(event=EventEnvelopeDTO.from_dict(tasks_completed), uow=uow)

    registration_completed = await session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.event_type == "registration.completed", OutboxEvent.aggregate_id == saga.id
        )
    )

    assert registration_completed is not None

    async with PostgreSQLAuthUnitOfWork(session=session) as uow:
        await handle_registration_completed(
            event=EventEnvelopeDTO.from_dict(
                {
                    "event_id": str(registration_completed.event_id),
                    "event_type": registration_completed.event_type,
                    "schema_version": registration_completed.schema_version,
                    "aggregate_id": str(registration_completed.aggregate_id),
                    "correlation_id": str(registration_completed.correlation_id),
                    "causation_id": str(registration_completed.causation_id),
                    "producer": registration_completed.producer,
                    "occurred_at": registration_completed.occurred_at.isoformat(),
                    "payload": registration_completed.payload,
                }
            ),
            uow=uow,
        )

    saga = await session.scalar(select(RegistrationSaga).where(RegistrationSaga.user_id == employee["user_id"]))

    assert saga is not None
    assert saga.status == RegistrationStatus.COMPLETED

    response = await org_client.get(f"/api/v1/companies/{company_id}/structure/{root_id}/employees", headers=headers)
    assert response.status_code == 200

    employees = response.json()["employees"]
    assert any(UUID(item["user_id"]) == employee["user_id"] for item in employees)
    response = await tasks_client.get(f"/api/v1/companies/{company_id}/tasks", headers=headers)
    assert response.status_code == 200

    tasks = response.json()["tasks"]

    assert any(task["title"] == "Welcome!" and str(employee["user_id"]) in task["assignee_ids"] for task in tasks)
