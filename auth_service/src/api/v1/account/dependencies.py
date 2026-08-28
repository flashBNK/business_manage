from container import Container
from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLAuthUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from usecases.auth.login.implementation import PostgreSQLLoginUseCase
from usecases.auth.logout.implementation import PostgreSQLLogoutUseCase
from usecases.auth.refresh.implementation import PostgreSQLRefreshUseCase
from usecases.profile.confirm_update_account.implementation import (
    PostgreSQLConfirmUpdateAccountUseCase,
)
from usecases.profile.list_accounts_user.implementation import (
    PostgreSQLListAccountsUserUseCase,
)
from usecases.profile.update_account.implementation import (
    PostgreSQLUpdateAccountUseCase,
)
from usecases.registration.check_account.implementation import (
    PostgreSQLCheckAccountUseCase,
)
from usecases.registration.complete.implementation import (
    PostgreSQLCompleteSignUpUseCase,
)
from usecases.registration.confirm_account.implementation import (
    PostgreSQLConfirmAccountUseCase,
)


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLAuthUnitOfWork:
    return build_unit_of_work(session)


def check_account_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCheckAccountUseCase(uow=uow)


def confirm_account_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLConfirmAccountUseCase(uow=uow)


def login_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLLoginUseCase(uow=uow, token_service=token_service)


def complete_sign_up_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLCompleteSignUpUseCase(uow=uow, token_service=token_service)


def list_accounts_user_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLListAccountsUserUseCase(uow=uow, token_service=token_service)


def update_account_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLUpdateAccountUseCase(uow=uow)


def confirm_update_account_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLConfirmUpdateAccountUseCase(uow=uow)


def refresh_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    token_service = Container.token_service()
    return PostgreSQLRefreshUseCase(uow=uow, token_service=token_service)


def logout_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLLogoutUseCase(uow=uow)
