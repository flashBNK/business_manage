from uuid import UUID

from domain.company_replica.models import CreateCompanyReplicaDTO
from domain.kafka.models import EventEnvelopeDTO
from domain.outbox_event.models import CreateOutboxEventDTO, OutboxEventType
from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm.models import CreateStructAdmDTO
from domain.struct_adm_position.exceptions import StructAdmPositionNotFound
from domain.struct_adm_position.models import CreateStructAdmPositionDTO
from domain.users_position.exceptions import UsersPositionNotFound
from domain.users_position.models import CreateUsersPositionDTO, GetUsersPositionDTO
from domain.users_replica.exceptions import UsersReplicaNotFound
from domain.users_replica.models import CreateUsersReplicaDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from logger import get_logger

log = get_logger(__name__)


async def handle_company_created(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    payload = event.payload
    company_dto = CreateCompanyReplicaDTO(name=payload["name"], company_id=UUID(payload["company_id"]))
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
        id=UUID(payload["user_id"]),
        username=payload["first_name"] + " " + payload["last_name"],
        company_id=UUID(payload["company_id"]),
        is_active=payload["is_active"],
        last_event_at=event.occurred_at,
    )
    log.info("user dto", dto=dto)
    await uow.users_replica.upsert(dto=dto)

    log.info("user successfully added to the database", payload=payload)


async def handle_registration_org_provision(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    payload = event.payload

    saga_id = UUID(payload["saga_id"])
    user_id = UUID(payload["user_id"])
    company_id = UUID(payload["company_id"])
    struct_adm_id = UUID(payload["struct_adm_id"])
    position_id = UUID(payload["position_id"])

    try:
        struct_adm_position = await uow.struct_adm_position.get_by_pair(
            dto=CreateStructAdmPositionDTO(struct_adm_id=struct_adm_id, position_id=position_id)
        )
        if struct_adm_position is None:
            raise StructAdmPositionNotFound

        try:
            users_position = await uow.users_position.get_for_check(
                dto=GetUsersPositionDTO(user_id=user_id, struct_adm_id=struct_adm_id, position_id=position_id),
                company_id=company_id,
            )
        except UsersPositionNotFound:
            users_position = None

        if users_position is None:
            users_position = await uow.users_position.create(
                dto=CreateUsersPositionDTO(user_id=user_id, struct_adm_id=struct_adm_id, position_id=position_id)
            )

            await uow.outbox_event.create(
                CreateOutboxEventDTO(
                    event_type=OutboxEventType.EMPLOYEE_POSITION_CHANGED,
                    aggregate_id=user_id,
                    correlation_id=event.correlation_id,
                    causation_id=event.event_id,
                    payload={
                        "user_id": str(user_id),
                        "struct_adm_id": str(struct_adm_id),
                        "company_id": str(company_id),
                        "position_id": str(position_id),
                        "role": str(users_position.role),
                    },
                )
            )

        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_ORG_COMPLETED,
                aggregate_id=saga_id,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
                payload={
                    "saga_id": str(saga_id),
                    "user_id": str(user_id),
                    "company_id": str(company_id),
                    "invite_id": payload["invite_id"],
                    "struct_adm_id": str(struct_adm_id),
                    "position_id": str(position_id),
                    "first_name": payload["first_name"],
                    "last_name": payload["last_name"],
                },
            )
        )

    except (PositionNotFound, StructAdmNotFound, StructAdmPositionNotFound, UsersReplicaNotFound) as exc:
        await uow.outbox_event.create(
            CreateOutboxEventDTO(
                event_type=OutboxEventType.REGISTRATION_ORG_FAILED,
                aggregate_id=saga_id,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
                payload={
                    "saga_id": str(saga_id),
                    "user_id": str(user_id),
                    "company_id": str(company_id),
                    "invite_id": payload["invite_id"],
                    "struct_adm_id": str(struct_adm_id),
                    "position_id": str(position_id),
                    "reason": str(exc),
                },
            )
        )


async def handle_registration_org_compensate(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    payload = event.payload

    saga_id = UUID(payload["saga_id"])
    user_id = UUID(payload["user_id"])
    company_id = UUID(payload["company_id"])
    struct_adm_id = UUID(payload["struct_adm_id"])
    position_id = UUID(payload["position_id"])

    dto = GetUsersPositionDTO(user_id=user_id, struct_adm_id=struct_adm_id, position_id=position_id)

    await uow.users_position.delete_by_dto(dto=dto)

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.EMPLOYEE_POSITION_DELETED,
            aggregate_id=user_id,
            correlation_id=event.correlation_id,
            causation_id=event.event_id,
            payload={
                "user_id": str(user_id),
                "struct_adm_id": str(struct_adm_id),
                "company_id": str(company_id),
                "position_id": str(position_id),
            },
        )
    )

    await uow.outbox_event.create(
        CreateOutboxEventDTO(
            event_type=OutboxEventType.REGISTRATION_ORG_COMPENSATED,
            aggregate_id=saga_id,
            correlation_id=event.correlation_id,
            causation_id=event.event_id,
            payload={
                "saga_id": str(saga_id),
                "user_id": str(user_id),
                "company_id": str(company_id),
                "struct_adm_id": str(struct_adm_id),
                "position_id": str(position_id),
            },
        )
    )


async def handle_employee_registration_failed(event: EventEnvelopeDTO, uow: PostgreSQLOrgUnitOfWork) -> None:
    user_id = UUID(event.payload["user_id"])
    await uow.users_replica.delete(users_replica_id=user_id)


EVENT_HANDLERS = {
    "company.created": handle_company_created,
    "employee.created": handle_employee_upsert,
    "employee.registered": handle_employee_upsert,
    "employee.registration.failed": handle_employee_registration_failed,
    "registration.org.provision": handle_registration_org_provision,
    "registration.org.compensate": handle_registration_org_compensate,
}
