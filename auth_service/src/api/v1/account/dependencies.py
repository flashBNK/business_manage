from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from container import Container
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork

from usecases.account.check_account.implementation import PostgreSQLCheckAccountUseCase
from usecases.account.confirm_account.implementation import PostgreSQLConfirmAccountUseCase
from usecases.account.login.implementation import PostgreSQLLoginUseCase
from usecases.account.sign_up_complete.implementation import PostgreSQLCompleteSignUpUseCase


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

def login_use_case(
    session: AsyncSession = Depends(get_async_session)
):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLLoginUseCase(uow=uow, token_service=token_service)

def complete_sign_up_use_case(
    session: AsyncSession = Depends(get_async_session)
):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLCompleteSignUpUseCase(uow=uow, token_service=token_service)