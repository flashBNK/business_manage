from domain.kafka.models import EventEnvelopeDTO
from infrastructure.databases.postgresql.models import UsersReplica
from infrastructure.databases.postgresql.models.company_replica import CompanyReplica
from logger import get_logger
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

log = get_logger("__name__")


async def handle_company_created(event: EventEnvelopeDTO, session: AsyncSession) -> None:
    payload = event.payload
    company = insert(CompanyReplica).values(id=payload["company_id"], name=payload["name"])
    stmt = company.on_conflict_do_update(index_elements=["id"], set_={"name": company.excluded.name})
    await session.execute(stmt)

    log.info("company successfully added to the database", company_name=payload["name"])


async def handle_employee_upsert(event: EventEnvelopeDTO, session: AsyncSession) -> None:
    payload = event.payload

    users_replica = insert(UsersReplica).values(
        id=payload["user_id"],
        username=payload["first_name"] + " " + payload["last_name"],
        company_id=payload["company_id"],
        last_event_at=event.occurred_at,
        is_active=payload["is_active"],
    )

    stmt = users_replica.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "username": users_replica.excluded.username,
            "company_id": users_replica.excluded.company_id,
            "is_active": users_replica.excluded.is_active,
            "last_event_at": users_replica.excluded.last_event_at,
            "deleted_at": None,
        },
    )
    await session.execute(stmt)

    log.info("user successfully added to the database", payload=payload)


EVENT_HANDLERS = {
    "company.created": handle_company_created,
    "employee.created": handle_employee_upsert,
    "employee.registered": handle_employee_upsert,
    # "employee.email_changed": handle_employee_email_changed,
}
