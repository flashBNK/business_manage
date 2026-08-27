import uuid

from domain.account.exceptions import EmailIsUsed
from domain.invite.exceptions import InvalidOrExpiredCode, InviteAlreadyUsed
from domain.invite.models import CompleteEmployeeInviteDTO
from domain.member.exceptions import MemberAlreadyActivated
from domain.member.models import CreateEmployeeDTO
from domain.token.models import TokenDTO
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from infrastructure.databases.postgresql.models.members import MemberRoles
from usecases.auth.employees.complete_invite.abstract import (
    AbstractCompleteEmployeeInviteUseCase,
)
from usecases.auth.employees.create.abstract import AbstractCreateEmployeeUseCase

from ..account.models import LoginResultSchema
from ..authorization import require_company_role
from .dependencies import complete_employee_invite_use_case, create_employee_use_case
from .models import (
    CompleteEmployeeInviteSchema,
    CreateEmployeeResultSchema,
    CreateEmployeeSchema,
)

router = APIRouter()


@router.post("/companies/{company_id}/employees", response_model=CreateEmployeeResultSchema)
async def create_employee(
    _request: Request,
    company_id: uuid.UUID,
    payload: CreateEmployeeSchema,
    _token: TokenDTO = Depends(require_company_role(MemberRoles.ADMIN)),
    usecase: AbstractCreateEmployeeUseCase = Depends(create_employee_use_case),
) -> JSONResponse:
    dto = CreateEmployeeDTO(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_id=company_id,
        role=payload.role,
    )

    try:
        result = await usecase.execute(dto)
    except EmailIsUsed as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from None

    result_schema = CreateEmployeeResultSchema(user_id=result.user_id, member_id=result.member_id)

    return JSONResponse(result_schema.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.post("/employees/invite-complete", response_model=CreateEmployeeResultSchema)
async def invite_complete(
    _request: Request,
    payload: CompleteEmployeeInviteSchema,
    usecase: AbstractCompleteEmployeeInviteUseCase = Depends(complete_employee_invite_use_case),
) -> JSONResponse:
    dto = CompleteEmployeeInviteDTO(
        invite_token=payload.invite_token,
        password=payload.password,
    )

    try:
        result = await usecase.execute(dto)
    except InvalidOrExpiredCode as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from None
    except (InviteAlreadyUsed, MemberAlreadyActivated) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from None

    result_schema = LoginResultSchema(access_token=result.access_token, refresh_token=result.refresh_token)

    return JSONResponse(result_schema.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)
