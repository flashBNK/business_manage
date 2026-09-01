from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from uscases.structure.managers.add.implementation import PostgreSQLAddManagerStructAdmUseCase
from uscases.structure.managers.delete.implementation import PostgreSQLDeleteManagerStructAdmUseCase
from uscases.structure.managers.get.implementation import PostgreSQLGetManagerStructAdmUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLOrgUnitOfWork:
    return build_unit_of_work(session)


def add_manager_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLAddManagerStructAdmUseCase(uow=uow)


def delete_manager_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeleteManagerStructAdmUseCase(uow=uow)


def get_manager_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetManagerStructAdmUseCase(uow=uow)
