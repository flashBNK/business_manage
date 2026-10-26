from uuid import UUID

from domain.position.exceptions import PositionNotFound
from domain.struct_adm.exceptions import StructAdmNotFound
from domain.struct_adm_position.models import CreateStructAdmPositionDTO, StructAdmPositionDTO
from domain.token.models import MemberRoles, TokenDTO
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse, Response
from uscases.struct_adm_position.create.abstract import AbstractCreateStructAdmPositionUseCase
from uscases.struct_adm_position.delete.abstract import AbstractDeleteStructAdmPositionUseCase
from uscases.struct_adm_position.list.abstract import AbstractListStructAdmPositionUseCase

from ..authorization import require_company_role
from .dependencies import (
    create_struct_adm_position_use_case,
    delete_struct_adm_position_use_case,
    list_struct_adm_position_use_case,
)
from .models import StructAdmPositionListSchema, StructAdmPositionSchema

router = APIRouter(prefix="/companies")


@router.post("/{company_id}/structure/{struct_adm_id}/positions/{position_id}", response_model=StructAdmPositionSchema)
async def create_struct_adm_position(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    position_id: UUID,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractCreateStructAdmPositionUseCase = Depends(create_struct_adm_position_use_case),
) -> JSONResponse:
    dto = CreateStructAdmPositionDTO(struct_adm_id=struct_adm_id, position_id=position_id)

    try:
        struct_adm_position = await usecase.execute(dto=dto, company_id=company_id)
    except (PositionNotFound, StructAdmNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(struct_adm_position).model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get("/{company_id}/structure/{struct_adm_id}/positions", response_model=StructAdmPositionListSchema)
async def list_struct_adm_positions(
    _request: Request,
    company_id: UUID,
    struct_adm_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    usecase: AbstractListStructAdmPositionUseCase = Depends(list_struct_adm_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        positions_page = await usecase.execute(
            company_id=company_id, struct_adm_id=struct_adm_id, limit=limit, offset=offset
        )
    except StructAdmNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    content = StructAdmPositionListSchema(
        total=positions_page.total,
        positions=[_to_schema(position).model_dump(mode="json") for position in positions_page.positions],
        limit=positions_page.limit,
        offset=positions_page.offset,
    )

    return JSONResponse(content.model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.delete("/{company_id}/structure/{struct_adm_id}/positions/{position_id}")
async def delete_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    struct_adm_id: UUID,
    usecase: AbstractDeleteStructAdmPositionUseCase = Depends(delete_struct_adm_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> Response:
    dto = StructAdmPositionDTO(struct_adm_id=struct_adm_id, position_id=position_id)
    try:
        await usecase.execute(company_id=company_id, dto=dto)
    except (PositionNotFound, StructAdmNotFound) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _to_schema(dto: StructAdmPositionDTO) -> StructAdmPositionSchema:
    return StructAdmPositionSchema(
        position_id=dto.position_id,
        struct_adm_id=dto.struct_adm_id,
    )
