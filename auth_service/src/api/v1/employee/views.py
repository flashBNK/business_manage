import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from domain.account.exceptions import EmailIsUsed
from domain.invite.exceptions import InvalidOrExpiredCode, InviteAlreadyUsed
from domain.invite.models import CompleteEmployeeInviteDTO
from domain.member.models import CreateEmployeeDTO
from domain.token.models import TokenDTO
from usecases.auth.employees.complete_invite.abstract import AbstractCompleteEmployeeInviteUseCase
from usecases.auth.employees.create.abstract import AbstractCreateEmployeeUseCase
from .models import CreateEmployeeSchema, CreateEmployeeResultSchema, CompleteEmployeeInviteSchema

from .dependencies import create_employee_use_case, complete_employee_invite_use_case
from ..account.models import LoginResultSchema
from ..token_dependencies import get_current_token

router = APIRouter()


@router.post("/companies/{company_id}/employees", response_model=CreateEmployeeResultSchema)
async def create_employee(
        request: Request,
        company_id: uuid.UUID,
        payload: CreateEmployeeSchema,
        token: TokenDTO = Depends(get_current_token),
        usecase: AbstractCreateEmployeeUseCase = Depends(create_employee_use_case),
) -> JSONResponse:

    for membership in token.memberships:
        if membership.company_id == company_id and membership.role == "admin":
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
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

            result_schema = CreateEmployeeResultSchema(user_id=result.user_id, member_id=result.member_id)

            return JSONResponse(result_schema.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to the requested resource is denied.")


@router.post("/employees/invite-complete", response_model=CreateEmployeeResultSchema)
async def invite_complete(
        request: Request,
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
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    except InviteAlreadyUsed as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))

    result_schema = LoginResultSchema(access_token=result.access_token)

    return JSONResponse(result_schema.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)
