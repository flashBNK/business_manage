from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork

from usecases.account.check_account.implementation import PostgreSQLCheckAccountUseCase
from usecases.account.confirm_account.implementation import PostgreSQLConfirmAccountUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session)
) -> PostgreSQLUnitOfWork:
    return build_unit_of_work(session)


def check_account_use_case(
    session: AsyncSession = Depends(get_async_session)
):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCheckAccountUseCase(uow=uow)


def confirm_account_use_case(
    session: AsyncSession = Depends(get_async_session)
):
    uow = get_unit_of_work(session=session)
    return PostgreSQLConfirmAccountUseCase(uow=uow)