from uuid import UUID

from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm.models import AddManagerStructAdmDTO, DeleteManagerStructAdmDTO, ManagerDTO
from domain.token.models import MemberRoles, TokenDTO
from domain.users_position.exceptions import UsersPositionNotFound
from domain.users_position.models import GetManagerDTO
from domain.users_replica.exceptions import UsersReplicaNotFound
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from uscases.managers.add.abstract import AbstractAddManagerStructAdmUseCase
from uscases.managers.delete.abstract import AbstractDeleteManagerStructAdmUseCase
from uscases.managers.get.abstract import AbstractGetManagerStructAdmUseCase

from ..authorization import require_company_role
from .dependencies import (
    add_manager_struct_adm_use_case,
    delete_manager_struct_adm_use_case,
    get_manager_struct_adm_use_case,
)
from .models import AddManagerStructAdmSchema, DeleteManagerStructAdmSchema, ManagerSchema

router = APIRouter(prefix="/companies")


@router.put("/{company_id}/structure/{struct_adm_id}/manager", response_model=ManagerSchema)
async def add_manager(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    payload: AddManagerStructAdmSchema,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractAddManagerStructAdmUseCase = Depends(add_manager_struct_adm_use_case),
) -> JSONResponse:
    dto = AddManagerStructAdmDTO(
        user_id=payload.user_id,
        struct_adm_id=struct_adm_id,
        position_id=payload.position_id,
    )

    try:
        manager = await usecase.execute(dto=dto, company_id=company_id)
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound, UsersPositionNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(manager).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.get("/{company_id}/structure/{struct_adm_id}/manager", response_model=ManagerSchema)
async def get_manager(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    usecase: AbstractGetManagerStructAdmUseCase = Depends(get_manager_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        manager = await usecase.execute(dto=GetManagerDTO(struct_adm_id=struct_adm_id, company_id=company_id))
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound, UsersPositionNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(manager).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.delete("/{company_id}/structure/{struct_adm_id}/manager", response_model=ManagerSchema)
async def delete_manager_struct_adm(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    payload: DeleteManagerStructAdmSchema,
    usecase: AbstractDeleteManagerStructAdmUseCase = Depends(delete_manager_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> JSONResponse:
    dto = DeleteManagerStructAdmDTO(
        struct_adm_id=struct_adm_id, position_id=payload.position_id, user_id=payload.user_id
    )
    try:
        manager = await usecase.execute(company_id=company_id, dto=dto)
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound, UsersPositionNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(manager).model_dump(mode="json"), status_code=status.HTTP_200_OK)


def _to_schema(dto: ManagerDTO) -> ManagerSchema:
    return ManagerSchema(
        user_id=dto.user_id,
        struct_adm_id=dto.struct_adm_id,
        position_id=dto.position_id,
        role=dto.role,
    )
