from uuid import UUID

from domain.company_replica.models import CreateCompanyReplicaDTO
from domain.kafka.models import EventEnvelopeDTO
from domain.struct_adm.models import CreateStructAdmDTO
from domain.users_replica.models import CreateUsersReplicaDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

log = get_logger("__name__")


async def handle_company_created(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    payload = event.payload
    company_dto = CreateCompanyReplicaDTO(name=payload["name"], company_id=payload["company_id"])
    await uow.company_replica.upsert(dto=company_dto)
    log.info("company successfully added to the database", company_name=payload["name"])

    dto = CreateStructAdmDTO(
        company_id=UUID(payload["company_id"]),
        name=payload["name"],
    )
    await uow.struct_adm.ensure_root(dto=dto)

    log.info("company_replica successfully added to the database", company_name=payload["name"])


async def handle_employee_upsert(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    payload = event.payload
    dto = CreateUsersReplicaDTO(
        id=payload["user_id"],
        username=payload["first_name"] + " " + payload["last_name"],
        company_id=payload["company_id"],
        is_active=payload["is_active"],
        last_event_at=event.occurred_at,
    )
    log.info("user dto", dto=dto)
    await uow.users_replica.upsert(dto=dto)

    log.info("user successfully added to the database", payload=payload)


EVENT_HANDLERS = {
    "company.created": handle_company_created,
    "employee.created": handle_employee_upsert,
    "employee.registered": handle_employee_upsert,
    # "employee.email_changed": handle_employee_email_changed,
}
