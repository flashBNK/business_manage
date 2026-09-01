from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from uscases.users_position.create.implementation import PostgreSQLCreateUsersPositionUseCase
from uscases.users_position.delete.implementation import PostgreSQLDeleteUsersPositionUseCase
from uscases.users_position.list_by_struct_adm.implementation import PostgreSQLListUsersPositionByStructAdmUseCase
from uscases.users_position.update.implementation import PostgreSQLUpdateUsersPositionUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLOrgUnitOfWork:
    return build_unit_of_work(session)


def create_users_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreateUsersPositionUseCase(uow=uow)


def list_users_position_by_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLListUsersPositionByStructAdmUseCase(uow=uow)


def delete_users_position_by_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeleteUsersPositionUseCase(uow=uow)


def update_users_position_by_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLUpdateUsersPositionUseCase(uow=uow)
