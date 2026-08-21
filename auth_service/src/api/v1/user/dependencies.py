from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from container import Container
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork

from usecases.profile.update_user.implementation import PostgreSQLUpdateUserUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session)
) -> PostgreSQLUnitOfWork:
    return build_unit_of_work(session)


def update_user_use_case(
    session: AsyncSession = Depends(get_async_session)
):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLUpdateUserUseCase(uow=uow, token_service=token_service)