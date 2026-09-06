from uuid import UUID

from domain.kafka.models import EventEnvelopeDTO
from domain.users_replica.models import CreateUsersReplicaDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from logger import get_logger

log = get_logger(__name__)


async def handle_employee_upsert(event: EventEnvelopeDTO, uow: PostgreSQLTasksUnitOfWork) -> None:
    payload = event.payload
    dto = CreateUsersReplicaDTO(
        id=UUID(payload["user_id"]),
        username=payload["first_name"] + " " + payload["last_name"],
        company_id=UUID(payload["company_id"]),
        is_active=payload["is_active"],
        last_event_at=event.occurred_at,
    )
    log.info("user dto", dto=dto)
    await uow.users_replica.upsert(dto=dto)

    log.info("user successfully added to the database", payload=payload)


EVENT_HANDLERS = {
    "employee.created": handle_employee_upsert,
    "employee.registered": handle_employee_upsert,
}
