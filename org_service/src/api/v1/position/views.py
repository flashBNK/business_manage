from uuid import UUID

from domain.position.exceptions import InvalidRequestPosition, PositionNotFound
from domain.position.models import CreatePositionDTO, PositionDTO, UpdatePositionDTO
from domain.token.models import MemberRoles, TokenDTO
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from uscases.position.create.abstract import AbstractCreatePositionUseCase
from uscases.position.delete.abstract import AbstractDeletePositionUseCase
from uscases.position.get.abstract import AbstractGetPositionUseCase
from uscases.position.list.abstract import AbstractListPositionUseCase
from uscases.position.update.abstract import AbstractUpdatePositionUseCase

from ..authorization import require_company_role
from .dependencies import (
    create_position_use_case,
    delete_position_use_case,
    get_position_use_case,
    list_position_use_case,
    update_position_use_case,
)
from .models import CreatePositionSchema, PositionSchema, UpdatePositionSchema

router = APIRouter(prefix="/companies")


@router.post("/{company_id}/positions", response_model=PositionSchema)
async def create_position(
    _request: Request,
    payload: CreatePositionSchema,
    company_id: UUID,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractCreatePositionUseCase = Depends(create_position_use_case),
) -> JSONResponse:
    dto = CreatePositionDTO(name=payload.name, company_id=company_id, description=payload.description)

    try:
        position = await usecase.execute(dto=dto)
    except InvalidRequestPosition as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(_to_schema(position).model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get("/{company_id}/positons", response_model=PositionSchema)
async def list_positions(
    _request: Request,
    company_id: UUID,
    usecase: AbstractListPositionUseCase = Depends(list_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        positions = await usecase.execute(company_id=company_id)
    except PositionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    content = {
        "total": len(positions),
        "positions": [_to_schema(position).model_dump(mode="json") for position in positions],
    }

    return JSONResponse(content, status_code=status.HTTP_200_OK)


@router.get("/{company_id}/positons/{position_id}", response_model=PositionSchema)
async def get_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    usecase: AbstractGetPositionUseCase = Depends(get_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        position = await usecase.execute(company_id=company_id, position_id=position_id)
    except PositionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(position).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.patch("/{company_id}/positons/{position_id}", response_model=PositionSchema)
async def update_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    payload: UpdatePositionSchema,
    usecase: AbstractUpdatePositionUseCase = Depends(update_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    dto = UpdatePositionDTO(name=payload.name, description=payload.description)
    try:
        position = await usecase.execute(company_id=company_id, dto=dto, position_id=position_id)
    except PositionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse(_to_schema(position).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.delete("/{company_id}/positons/{position_id}", response_model=PositionSchema)
async def delete_positions(
    _request: Request,
    company_id: UUID,
    position_id: UUID,
    usecase: AbstractDeletePositionUseCase = Depends(delete_position_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        await usecase.execute(company_id=company_id, position_id=position_id)
    except PositionNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from None

    return JSONResponse({}, status_code=status.HTTP_204_NO_CONTENT)


def _to_schema(dto: PositionDTO) -> PositionSchema:
    return PositionSchema(
        id=dto.id,
        name=dto.name,
        company_id=dto.company_id,
        description=dto.description,
    )
