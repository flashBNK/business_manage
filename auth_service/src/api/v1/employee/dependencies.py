from container import Container
from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from usecases.auth.employees.complete_invite.implementation import (
    PostgreSQLCompleteEmployeeInviteUseCase,
)
from usecases.auth.employees.create.implementation import (
    PostgreSQLCreateEmployeeUseCase,
)


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLAuthUnitOfWork:
    return build_unit_of_work(session)


def create_employee_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreateEmployeeUseCase(uow=uow)


def complete_employee_invite_use_case(
    session: AsyncSession = Depends(get_async_session),
):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLCompleteEmployeeInviteUseCase(uow=uow, token_service=token_service)
