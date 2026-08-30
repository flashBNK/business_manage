from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from uscases.position.create.implementation import PostgreSQLCreatePositionUseCase
from uscases.position.delete.implementation import PostgreSQLDeletePositionUseCase
from uscases.position.get.implementation import PostgreSQLGetPositionUseCase
from uscases.position.list.implementation import PostgreSQLListPositionUseCase
from uscases.position.update.implementation import PostgreSQLUpdatePositionUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLOrgUnitOfWork:
    return build_unit_of_work(session)


def create_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreatePositionUseCase(uow=uow)


def list_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLListPositionUseCase(uow=uow)


def get_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetPositionUseCase(uow=uow)


def update_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLUpdatePositionUseCase(uow=uow)


def delete_position_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeletePositionUseCase(uow=uow)
