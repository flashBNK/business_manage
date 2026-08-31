from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from uscases.struct_adm_position.create.implementation import PostgreSQLCreateStructAdmPositionUseCase
from uscases.struct_adm_position.delete.implementation import PostgreSQLDeleteStructAdmPositionUseCase
from uscases.struct_adm_position.list.implementation import PostgreSQLListStructAdmPositionUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLOrgUnitOfWork:
    return build_unit_of_work(session)


def create_struct_adm_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreateStructAdmPositionUseCase(uow=uow)


def list_struct_adm_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLListStructAdmPositionUseCase(uow=uow)


def delete_struct_adm_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeleteStructAdmPositionUseCase(uow=uow)
