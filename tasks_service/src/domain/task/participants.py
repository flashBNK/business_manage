from uuid import UUID

from domain.task.exceptions import ParticipantInactive, ParticipantWrongCompany, ParticipantNotFound
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork


async def check_participant(user_id: UUID, company_id: UUID, uow: PostgreSQLTasksUnitOfWork) -> None:
    participant = await uow.users_replica.get(user_id)

    if participant is None:
        raise ParticipantNotFound
    if not participant.is_active:
        raise ParticipantInactive
    if participant.company_id != company_id:
        raise ParticipantWrongCompany


async def validate_participant(
    author_id: UUID,
    responsible_id: UUID,
    watcher_ids: list[UUID],
    assignee_ids: list[UUID],
    company_id: UUID,
    uow: PostgreSQLTasksUnitOfWork,
) -> None:
    user_ids = {author_id, responsible_id, *watcher_ids, *assignee_ids}
    for user_id in user_ids:
        await check_participant(user_id, company_id, uow)