import asyncio
import json
import os
import uuid
from types import SimpleNamespace
from uuid import UUID

import pytest_asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from httpx import AsyncClient
from infrastructure.databases.postgresql.models.invite import Invite
from infrastructure.databases.postgresql.models.outbox_event import OutboxEvent
from sqlalchemy import select

from ..integration.register_user import register_user

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

EVENT_TOPICS = {
    "company.created": "auth.company.events",
    "employee.created": "auth.employee.events",
    "employee.registered": "auth.employee.events",
    "registration.org.provision": "registration.org.commands",
    "registration.org.compensate": "registration.org.commands",
    "registration.tasks.provision": "registration.tasks.commands",
}


@pytest_asyncio.fixture()
async def org_client():
    async with AsyncClient(base_url="http://127.0.0.1:8001") as client:
        yield client


@pytest_asyncio.fixture()
async def tasks_client():
    async with AsyncClient(base_url="http://127.0.0.1:8002") as client:
        yield client


@pytest_asyncio.fixture()
async def kafka():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    consumer = AIOKafkaConsumer(
        "registration.saga.events",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=f"saga-tests-{uuid.uuid4()}",
        auto_offset_reset="earliest",
    )

    await producer.start()
    await consumer.start()

    async def publish(event: dict) -> None:
        topic = EVENT_TOPICS[event["event_type"]]

        await producer.send_and_wait(topic=topic, key=event["aggregate_id"].encode(), value=json.dumps(event).encode())

    async def wait_for_event(event_type: str, correlation_id: UUID, timeout: float = 30) -> dict:
        async with asyncio.timeout(timeout):
            async for message in consumer:
                event = json.loads(message.value)

                if event["event_type"] == event_type and event["correlation_id"] == str(correlation_id):
                    return event

        raise AssertionError(f"Event={event_type}, correlation_id={correlation_id}")

    try:
        yield SimpleNamespace(publish=publish, wait_for_event=wait_for_event)
    finally:
        await consumer.stop()
        await producer.stop()


@pytest_asyncio.fixture()
async def admin(client, session):
    return await register_user(
        client,
        session,
        email=f"admin-{uuid.uuid4()}@example.com",
        password="AdminPassword123!",
        first_name="Admin",
        last_name="User",
        company_name=f"Company-{uuid.uuid4()}",
    )


def outbox_to_event(event: OutboxEvent) -> dict:
    return {
        "event_id": str(event.event_id),
        "event_type": event.event_type,
        "schema_version": event.schema_version,
        "aggregate_id": str(event.aggregate_id),
        "correlation_id": str(event.correlation_id),
        "causation_id": str(event.causation_id) if event.causation_id else None,
        "producer": event.producer,
        "occurred_at": event.occurred_at.isoformat(),
        "payload": event.payload,
    }


async def publish_outbox_event(session, kafka, event_type: str, aggregate_id: UUID) -> OutboxEvent:
    event = await session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_type == event_type, OutboxEvent.aggregate_id == aggregate_id)
    )
    assert event is not None

    await kafka.publish(outbox_to_event(event))

    return event


async def get_root_structure(org_client, company_id: UUID, access_token: str) -> UUID:
    headers = {"Authorization": f"Bearer {access_token}"}

    async with asyncio.timeout(30):
        while True:
            response = await org_client.get(f"/api/v1/companies/{company_id}/structure", headers=headers)

            if response.status_code == 200:
                structure = response.json()

                if structure["children"]:
                    return UUID(structure["children"][0]["id"])

            await asyncio.sleep(0.2)

    raise AssertionError("Root structure не создан")


async def create_employee(client, session, admin: dict, struct_adm_id: UUID, position_id: UUID) -> dict:
    email = f"employee-{uuid.uuid4()}@example.com"
    password = "EmployeePassword123!"

    response = await client.post(
        f"/api/v1/companies/{admin['company_id']}/employees",
        json={
            "email": email,
            "first_name": "Employee",
            "last_name": "User",
            "role": "member",
            "struct_adm_id": str(struct_adm_id),
            "position_id": str(position_id),
        },
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert response.status_code == 201

    user_id = UUID(response.json()["user_id"])

    invite = await session.scalar(select(Invite).where(Invite.user_id == user_id))
    assert invite is not None

    return {
        "user_id": user_id,
        "email": email,
        "password": password,
        "invite": invite,
    }


def make_event(
    event_type: str,
    aggregate_id: UUID,
    correlation_id: UUID,
    payload: dict,
) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "schema_version": 1,
        "aggregate_id": str(aggregate_id),
        "correlation_id": str(correlation_id),
        "causation_id": None,
        "producer": "tasks_service",
        "occurred_at": "2026-01-01T00:00:00+00:00",
        "payload": payload,
    }
