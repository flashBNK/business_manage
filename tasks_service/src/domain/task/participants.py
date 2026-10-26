from uuid import UUID

from domain.task.exceptions import ParticipantInactive, ParticipantNotFound, ParticipantWrongCompany
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork


async def check_participant(user_ids: list[UUID], company_id: UUID, uow: PostgreSQLTasksUnitOfWork) -> None:
    unique_ids = list(dict.fromkeys(user_ids))

    if not unique_ids:
        return

    participants = await uow.users_replica.list_by_ids(user_ids=unique_ids)
    participants_by_id = {participant.id: participant for participant in participants}

    for user_id in unique_ids:
        participant = participants_by_id.get(user_id)

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
    await check_participant(
        user_ids=[author_id, responsible_id, *watcher_ids, *assignee_ids], company_id=company_id, uow=uow
    )
