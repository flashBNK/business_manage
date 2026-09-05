from uuid import UUID

from sqlalchemy.exc import IntegrityError

from domain.struct_adm.exceptions import InvalidRequestStructAdm, NodeHasDependentsException, NodeHasRootStructAdm, \
    StructAdmHasUsers
from domain.struct_adm.models import (
    CompanyStructureDTO,
    CreateStructAdmDTO,
    MoveStructAdmDTO,
    StructAdmDTO,
    StructAdmTreeDTO,
    UpdateStructAdmDTO,
)
from domain.token.models import MemberRoles, TokenDTO
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from uscases.structure.struct_adm.create.abstract import AbstractCreateStructAdmUseCase
from uscases.structure.struct_adm.delete.abstract import AbstractDeleteStructAdmUseCase
from uscases.structure.struct_adm.get.abstract import AbstractGetStructAdmUseCase
from uscases.structure.struct_adm.get_ancestors.abstract import AbstractGetAncestorsStructAdmUseCase
from uscases.structure.struct_adm.get_children.abstract import AbstractGetChildrenStructAdmUseCase
from uscases.structure.struct_adm.get_company_structure.abstract import AbstractGetCompanyStructureUseCase
from uscases.structure.struct_adm.get_descendants.abstract import AbstractGetDescendantsStructAdmUseCase
from uscases.structure.struct_adm.move.abstract import AbstractMoveStructAdmUseCase
from uscases.structure.struct_adm.rename.abstract import AbstractRenameStructAdmUseCase

from ..authorization import require_company_role
from .dependencies import (
    create_struct_adm_use_case,
    delete_struct_adm_use_case,
    get_ancestors_use_case,
    get_children_use_case,
    get_company_structure_use_case,
    get_descendants_use_case,
    get_struct_adm_use_case,
    move_struct_adm_use_case,
    rename_struct_adm_use_case,
)
from .models import (
    CompanyStructureSchema,
    CreateStructAdmSchema,
    MoveStructAdmSchema,
    StructAdmSchema,
    StructAdmTreeSchema,
)

router = APIRouter(prefix="/companies")


@router.post("/{company_id}/structure/{parent_id}/children", response_model=StructAdmSchema)
async def create_struct_adm(
    _request: Request,
    payload: CreateStructAdmSchema,
    company_id: UUID,
    parent_id: UUID,
    _token: TokenDTO = Depends(require_company_role(min_role=MemberRoles.ADMIN)),
    usecase: AbstractCreateStructAdmUseCase = Depends(create_struct_adm_use_case),
) -> JSONResponse:
    dto = CreateStructAdmDTO(name=payload.name, company_id=company_id)

    try:
        struct_adm = await usecase.execute(dto=dto, parent_id=parent_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(_to_schema(struct_adm).model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get("/{company_id}/structure/{struct_adm_id}", response_model=StructAdmSchema)
async def get_struct_adm(
    _request: Request,
    struct_adm_id: UUID,
    company_id: UUID,
    usecase: AbstractGetStructAdmUseCase = Depends(get_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        struct_adm = await usecase.execute(struct_adm_id=struct_adm_id, company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(_to_schema(struct_adm).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.get("/{company_id}/structure/{parent_id}/children", response_model=StructAdmSchema)
async def get_children(
    _request: Request,
    parent_id: UUID,
    company_id: UUID,
    usecase: AbstractGetChildrenStructAdmUseCase = Depends(get_children_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        children = await usecase.execute(parent_id=parent_id, company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        [_to_schema(children).model_dump(mode="json") for children in children], status_code=status.HTTP_200_OK
    )


@router.get("/{company_id}/structure/{parent_id}/descendants", response_model=StructAdmSchema)
async def get_descendants(
    _request: Request,
    parent_id: UUID,
    company_id: UUID,
    usecase: AbstractGetDescendantsStructAdmUseCase = Depends(get_descendants_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        descendants = await usecase.execute(parent_id=parent_id, company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        [_to_schema(descendant).model_dump(mode="json") for descendant in descendants], status_code=status.HTTP_200_OK
    )


@router.get("/{company_id}/structure/{struct_adm_id}/ancestors", response_model=StructAdmSchema)
async def get_ancestors(
    _request: Request,
    struct_adm_id: UUID,
    company_id: UUID,
    usecase: AbstractGetAncestorsStructAdmUseCase = Depends(get_ancestors_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        ancestors = await usecase.execute(struct_adm_id=struct_adm_id, company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        [_to_schema(ancestor).model_dump(mode="json") for ancestor in ancestors], status_code=status.HTTP_200_OK
    )


@router.patch("/{company_id}/structure/{struct_adm_id}", response_model=StructAdmSchema)
async def rename_struct_adm(
    _request: Request,
    struct_adm_id: UUID,
    company_id: UUID,
    payload: CreateStructAdmSchema,
    usecase: AbstractRenameStructAdmUseCase = Depends(rename_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> JSONResponse:
    dto = UpdateStructAdmDTO(name=payload.name)
    try:
        struct_adm = await usecase.execute(struct_adm_id=struct_adm_id, company_id=company_id, dto=dto)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(_to_schema(struct_adm).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.patch("/{company_id}/structure/{struct_adm_id}/move", response_model=StructAdmSchema)
async def move_struct_adm(
    _request: Request,
    struct_adm_id: UUID,
    company_id: UUID,
    payload: MoveStructAdmSchema,
    usecase: AbstractMoveStructAdmUseCase = Depends(move_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> JSONResponse:
    dto = MoveStructAdmDTO(new_parent_id=payload.new_parent_id)
    try:
        struct_adm = await usecase.execute(struct_adm_id=struct_adm_id, company_id=company_id, dto=dto)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(_to_schema(struct_adm).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.delete("/{company_id}/structure/{struct_adm_id}")
async def delete_struct_adm(
    _request: Request,
    struct_adm_id: UUID,
    company_id: UUID,
    usecase: AbstractDeleteStructAdmUseCase = Depends(delete_struct_adm_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
) -> Response:
    try:
        await usecase.execute(struct_adm_id=struct_adm_id, company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None
    except (NodeHasDependentsException, NodeHasRootStructAdm, StructAdmHasUsers) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{company_id}/structure", response_model=CompanyStructureSchema)
async def get_company_structure(
    _request: Request,
    company_id: UUID,
    usecase: AbstractGetCompanyStructureUseCase = Depends(get_company_structure_use_case),
    _token: TokenDTO = Depends(require_company_role(MemberRoles.MEMBER)),
) -> JSONResponse:
    try:
        structure = await usecase.execute(company_id=company_id)
    except InvalidRequestStructAdm as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    return JSONResponse(
        _to_schema_company_structure(structure).model_dump(mode="json"), status_code=status.HTTP_200_OK
    )


def _to_schema(dto: StructAdmDTO) -> StructAdmSchema:
    return StructAdmSchema(
        id=dto.id,
        name=dto.name,
        company_id=dto.company_id,
        path=dto.path,
    )


def _to_schema_struct_adm_tree(structure_tree: StructAdmTreeDTO) -> StructAdmTreeSchema:
    return StructAdmTreeSchema(
        id=structure_tree.id,
        name=structure_tree.name,
        children=[_to_schema_struct_adm_tree(child) for child in structure_tree.children],
    )


def _to_schema_company_structure(
    dto: CompanyStructureDTO,
) -> CompanyStructureSchema:
    return CompanyStructureSchema(
        id=dto.id,
        name=dto.name,
        children=[_to_schema_struct_adm_tree(child) for child in dto.children],
    )
