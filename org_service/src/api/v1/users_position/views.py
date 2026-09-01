from uuid import UUID

from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.token.models import MemberRoles, TokenDTO
from domain.users_position.exceptions import UsersPositionNotFound
from domain.users_position.models import (
    CreateUsersPositionDTO,
    EmployeePositionDTO,
    GetUsersPositionDTO,
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)
from domain.users_replica.exceptions import UsersReplicaNotFound
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from uscases.users_position.create.abstract import AbstractCreateUsersPositionUseCase
from uscases.users_position.delete.abstract import AbstractDeleteUsersPositionUseCase
from uscases.users_position.list_by_struct_adm.abstract import AbstractListUsersPositionByStructAdmUseCase
from uscases.users_position.update.abstract import AbstractUpdateUsersPositionUseCase

from ..authorization import require_company_role
from ..structure.views import _to_schema as _to_schema_struct_adm
from .dependencies import (
    create_users_position_use_case,
    delete_users_position_by_struct_adm_use_case,
    list_users_position_by_struct_adm_use_case,
    update_users_position_by_struct_adm_use_case,
)
from .models import CreateUsersPositionSchema, EmployeePositionSchema, UpdateUsersPositionSchema, UsersPositionSchema

router = APIRouter(prefix="/companies")


@router.post("/{company_id}/structure/{struct_adm_id}/employees", response_model=UsersPositionSchema)
async def create_users_position(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    payload: CreateUsersPositionSchema,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractCreateUsersPositionUseCase = Depends(create_users_position_use_case),
) -> JSONResponse:
    dto = CreateUsersPositionDTO(
        user_id=payload.user_id,
        struct_adm_id=struct_adm_id,
        position_id=payload.position_id,
        role=payload.role,
    )

    try:
        users_position = await usecase.execute(dto=dto, company_id=company_id)
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(
        _to_schema_users_position(users_position).model_dump(mode="json"), status_code=status.HTTP_201_CREATED
    )


@router.get("/{company_id}/structure/{struct_adm_id}/employees", response_model=EmployeePositionSchema)
async def list_by_struct_adm(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    include_children: bool = False,
    usecase: AbstractListUsersPositionByStructAdmUseCase = Depends(list_users_position_by_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        employees, struct_adm = await usecase.execute(
            company_id=company_id, struct_adm_id=struct_adm_id, include_children=include_children
        )
    except (PositionNotFound, StructAdmNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    content = {
        "struct_adm": _to_schema_struct_adm(struct_adm).model_dump(mode="json"),
        "total": len(employees),
        "employees": [_to_schema_employee_position(employee).model_dump(mode="json") for employee in employees],
    }

    return JSONResponse(content, status_code=status.HTTP_200_OK)


@router.delete(
    "/{company_id}/structure/{struct_adm_id}/positions/{position_id}/employees/{user_id}",
    response_model=UsersPositionSchema,
)
async def delete_users_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    struct_adm_id: UUID,
    user_id: UUID,
    usecase: AbstractDeleteUsersPositionUseCase = Depends(delete_users_position_by_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> Response:
    dto = GetUsersPositionDTO(struct_adm_id=struct_adm_id, position_id=position_id, user_id=user_id)
    try:
        await usecase.execute(company_id=company_id, dto=dto)
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{company_id}/structure/{struct_adm_id}/positions/{position_id}/employees/{user_id}",
    response_model=UsersPositionSchema,
)
async def update_users_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    struct_adm_id: UUID,
    user_id: UUID,
    payload: UpdateUsersPositionSchema,
    usecase: AbstractUpdateUsersPositionUseCase = Depends(update_users_position_by_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> JSONResponse:
    dto = UpdateUsersPositionDTO(
        user_id=user_id,
        old_position_id=position_id,
        old_struct_adm_id=struct_adm_id,
        new_struct_adm_id=payload.struct_adm_id,
        new_position_id=payload.position_id,
        new_role=payload.role,
    )
    try:
        users_position = await usecase.execute(company_id=company_id, dto=dto)
    except (PositionNotFound, StructAdmNotFound, UsersReplicaNotFound, UsersPositionNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(
        _to_schema_users_position(users_position).model_dump(mode="json"), status_code=status.HTTP_200_OK
    )


def _to_schema_users_position(dto: UsersPositionDTO) -> UsersPositionSchema:
    return UsersPositionSchema(
        user_id=dto.user_id,
        position_id=dto.position_id,
        struct_adm_id=dto.struct_adm_id,
        role=dto.role,
    )


def _to_schema_employee_position(dto: EmployeePositionDTO) -> EmployeePositionSchema:
    return EmployeePositionSchema(
        user_id=dto.user_id,
        username=dto.username,
        position_id=dto.position_id,
        position_name=dto.position_name,
        role=dto.role,
    )
