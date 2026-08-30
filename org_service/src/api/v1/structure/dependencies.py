from fastapi import Depends
from infrastructure.databases.postgresql.session import get_async_session
from infrastructure.di.injection import build_unit_of_work
from infrastructure.repositories.postgresql.uow import PostgreSQLOrgUnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession
from uscases.structure.struct_adm.create.implementation import PostgreSQLCreateStructAdmUseCase
from uscases.structure.struct_adm.delete.implementation import PostgreSQLDeleteStructAdmUseCase
from uscases.structure.struct_adm.get.implementation import PostgreSQLGetStructAdmUseCase
from uscases.structure.struct_adm.get_ancestors.implementation import PostgreSQLGetAncestorsUseCase
from uscases.structure.struct_adm.get_children.implementation import PostgreSQLGetChildrenUseCase
from uscases.structure.struct_adm.get_descendants.implementation import PostgreSQLGetDescendantsUseCase
from uscases.structure.struct_adm.move.implementation import PostgreSQLMoveStructAdmUseCase
from uscases.structure.struct_adm.rename.implementation import PostgreSQLRenameStructAdmUseCase


def get_unit_of_work(
    session: AsyncSession = Depends(get_async_session),
) -> PostgreSQLOrgUnitOfWork:
    return build_unit_of_work(session)


def create_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLCreateStructAdmUseCase(uow=uow)


def get_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetStructAdmUseCase(uow=uow)


def get_children_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetChildrenUseCase(uow=uow)


def get_descendants_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetDescendantsUseCase(uow=uow)


def get_ancestors_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLGetAncestorsUseCase(uow=uow)


def rename_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLRenameStructAdmUseCase(uow=uow)


def move_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLMoveStructAdmUseCase(uow=uow)


def delete_struct_adm_use_case(session: AsyncSession = Depends(get_async_session)):
    uow = get_unit_of_work(session=session)
    return PostgreSQLDeleteStructAdmUseCase(uow=uow)


# def login_use_case(session: AsyncSession = Depends(get_async_session)):
#     uow = get_unit_of_work(session=session)
#     token_service = Container.token_service()
#     return PostgreSQLLoginUseCase(uow=uow, token_service=token_service)
