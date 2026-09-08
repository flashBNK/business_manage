from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLTasksUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession

from usecases.task.change_status.implementation import PostgreSQLChangeStatusTaskUseCase
from usecases.task.create.implementation import PostgreSQLCreateTaskUseCase
from usecases.task.delete.implementation import PostgreSQLDeleteTaskUseCase
from usecases.task.get.implementation import PostgreSQLGetTaskUseCase
from usecases.task.list.implementation import PostgreSQLListTaskUseCase
from usecases.task.update.implementation import PostgreSQLUpdateTaskUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLTasksUnitOfWork:
    return build_unit_of_work(session)


def create_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreateTaskUseCase(uow=uow)


def get_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetTaskUseCase(uow=uow)


def list_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLListTaskUseCase(uow=uow)


def update_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLUpdateTaskUseCase(uow=uow)


def change_status_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLChangeStatusTaskUseCase(uow=uow)


def delete_task_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeleteTaskUseCase(uow=uow)