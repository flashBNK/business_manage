from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from domain.account.exceptions import EmailIsUsed
from domain.account.models import CreateAccountDTO, AccountDTO, ConfirmAccountDTO
from domain.invite.exceptions import InvalidOrExpiredCode, TooManyAttempts
from usecases.account.check_account.abstract import AbstractCheckAccountUseCase
from usecases.account.confirm_account.abstract import AbstractConfirmAccountUseCase

from .dependencies import check_account_use_case, confirm_account_use_case
from .models import CreateAccountSchema, AccountSchema, ConfirmAccountSchema

router = APIRouter()


@router.post("/check_account", response_model=CreateAccountSchema)
async def check_account(
        request: Request,
        payload: CreateAccountSchema,
        usecase: AbstractCheckAccountUseCase = Depends(check_account_use_case),
) -> JSONResponse:
    dto = CreateAccountDTO(email=payload.email)

    try:
        await usecase.execute(dto)
    except EmailIsUsed as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.post("/sign-up", response_model=AccountSchema)
async def confirm_account(
        request: Request,
        payload: ConfirmAccountSchema,
        usecase: AbstractConfirmAccountUseCase = Depends(confirm_account_use_case),
) -> JSONResponse:
    dto = ConfirmAccountDTO(
        email=payload.email,
        code=payload.code,
    )

    try:
        account = await usecase.execute(dto)
    except InvalidOrExpiredCode as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except TooManyAttempts as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

    return JSONResponse(_to_schema(account).model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


def _to_schema(dto: AccountDTO):
    return AccountSchema(
        id=dto.id,
        email=dto.email,
        is_verified=dto.is_verified,
        verified_at=dto.verified_at,
    )