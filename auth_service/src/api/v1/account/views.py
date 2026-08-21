from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from domain.account.exceptions import EmailIsUsed, EmailNotFound, AccountAlreadyRegistered
from domain.account.models import CreateAccountDTO, AccountDTO, ConfirmAccountDTO, CompleteSignUpDTO
from domain.invite.exceptions import InvalidOrExpiredCode, TooManyAttempts
from domain.secret.exceptions import WrongSecretPassword, SecretNotFound
from domain.token.models import LoginDTO, TokenDTO
from usecases.registration.check_account.abstract import AbstractCheckAccountUseCase
from usecases.registration.confirm_account.abstract import AbstractConfirmAccountUseCase
from usecases.auth.login.abstract import AbstractLoginUseCase
from usecases.registration.complete.abstract import AbstractCompleteSignUpUseCase

from .dependencies import check_account_use_case, confirm_account_use_case, login_use_case, complete_sign_up_use_case
from .models import CreateAccountSchema, AccountSchema, ConfirmAccountSchema, LoginSchema, LoginResultSchema, \
    CompleteSingUpSchema
from ..token_dependencies import get_current_token

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


@router.post("/login", response_model=LoginSchema)
async def login(
        request: Request,
        payload: LoginSchema,
        usecase: AbstractLoginUseCase = Depends(login_use_case),
) -> JSONResponse:
    dto = LoginDTO(
        email=payload.email,
        password=payload.password,
    )

    try:
        token = await usecase.execute(dto)
    except (WrongSecretPassword, EmailNotFound):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    except SecretNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return JSONResponse(LoginResultSchema(access_token=token.access_token).model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.post("/sign-up-complete", response_model=LoginResultSchema)
async def complete_sign_up(
        request: Request,
        payload: CompleteSingUpSchema,
        usecase: AbstractCompleteSignUpUseCase = Depends(complete_sign_up_use_case)
) -> JSONResponse:
    dto = CompleteSignUpDTO(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_name=payload.company_name if payload.company_name else None,
    )

    try:
        result = await usecase.execute(dto)
    except (EmailNotFound, ) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except AccountAlreadyRegistered as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    token = LoginResultSchema(access_token=result.access_token)

    return JSONResponse(token.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get("/me")
async def me(
        token: TokenDTO = Depends(get_current_token)
) -> dict:
    content = {"User": token.subject, "memberships": token.memberships}
    return content


def _to_schema(dto: AccountDTO):
    return AccountSchema(
        id=dto.id,
        email=dto.email,
        is_verified=dto.is_verified,
        verified_at=dto.verified_at,
    )