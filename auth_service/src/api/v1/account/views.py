import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from domain.account.exceptions import EmailIsUsed, EmailNotFound, AccountAlreadyRegistered, AccountNotFound, \
    AccountForbidden
from domain.account.models import CreateAccountDTO, AccountDTO, ConfirmAccountDTO, CompleteSignUpDTO, \
    RequestEmailChangeDTO, ConfirmEmailChangeDTO
from domain.invite.exceptions import InvalidOrExpiredCode, TooManyAttempts
from domain.refresh_token.exceptions import InvalidRefreshToken
from domain.secret.exceptions import WrongSecretPassword, SecretNotFound
from domain.token.models import LoginDTO, TokenDTO
from usecases.auth.logout.abstract import AbstractLogoutUseCase
from usecases.auth.refresh.abstract import AbstractRefreshUseCase
from usecases.profile.confirm_update_account.abstract import AbstractConfirmUpdateAccountUseCase
from usecases.profile.list_accounts_user.abstract import AbstractListAccountsUserUseCase
from usecases.profile.update_account.abstract import AbstractUpdateAccountUseCase
from usecases.registration.check_account.abstract import AbstractCheckAccountUseCase
from usecases.registration.confirm_account.abstract import AbstractConfirmAccountUseCase
from usecases.auth.login.abstract import AbstractLoginUseCase
from usecases.registration.complete.abstract import AbstractCompleteSignUpUseCase

from .dependencies import check_account_use_case, confirm_account_use_case, login_use_case, complete_sign_up_use_case, \
    list_accounts_user_use_case, update_account_use_case, confirm_update_account_use_case, refresh_use_case, \
    logout_use_case
from .models import CreateAccountSchema, AccountSchema, ConfirmAccountSchema, LoginSchema, LoginResultSchema, \
    CompleteSingUpSchema, ListAccountsSchema, RequestEmailChangeSchema, ConfirmSchema, RefreshSchema
from ..token_dependencies import get_current_token

router = APIRouter()


@router.post("/check_account", response_model=CreateAccountSchema)
async def check_account(
        _request: Request,
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
        _request: Request,
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
        _request: Request,
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

    content = LoginResultSchema(access_token=token.access_token, refresh_token=token.refresh_token)

    return JSONResponse(content.model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.post("/sign-up-complete", response_model=LoginResultSchema)
async def complete_sign_up(
        _request: Request,
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

    token = LoginResultSchema(access_token=result.access_token, refresh_token=result.refresh_token)

    return JSONResponse(token.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get("/me")
async def me(
        _request: Request,
        token: TokenDTO = Depends(get_current_token)
) -> dict:
    content = {"User": token.subject, "memberships": token.memberships}
    return content


@router.get("/me/accounts", response_model=ListAccountsSchema)
async def list_accounts_user(
        _request: Request,
        token: TokenDTO = Depends(get_current_token),
        usecase: AbstractListAccountsUserUseCase = Depends(list_accounts_user_use_case),
) -> JSONResponse:
    accounts, total = await usecase.execute(user_id=token.subject)

    content = ListAccountsSchema(
        total=total,
        accounts=[_to_schema(account) for account in accounts],
    )

    return JSONResponse(content.model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.post("/account/{account_id}")
async def update_account(
        _request: Request,
        account_id: uuid.UUID,
        payload: RequestEmailChangeSchema,
        token: TokenDTO = Depends(get_current_token),
        usecase: AbstractUpdateAccountUseCase = Depends(update_account_use_case)
) -> JSONResponse:
    dto = RequestEmailChangeDTO(
        user_id=token.subject,
        new_email=payload.new_email,
    )

    try:
        await usecase.execute(dto=dto, account_id=account_id)
    except AccountNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    except AccountForbidden as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc)
    except EmailIsUsed as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return JSONResponse({}, status_code=status.HTTP_201_CREATED)


@router.post("/account/{account_id}/update-complete", response_model=AccountSchema)
async def update_account_complete(
        _request: Request,
        account_id: uuid.UUID,
        payload: ConfirmSchema,
        token: TokenDTO = Depends(get_current_token),
        usecase: AbstractConfirmUpdateAccountUseCase = Depends(confirm_update_account_use_case)
) -> JSONResponse:
    dto = ConfirmEmailChangeDTO(
        user_id=token.subject,
        account_id=account_id,
        invite_code=payload.invite_code,
    )

    try:
        account = await usecase.execute(dto=dto)
    except InvalidOrExpiredCode:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Incorrect code")
    except AccountForbidden:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not found")

    return JSONResponse(_to_schema(account).model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.post("/refresh", response_model=LoginResultSchema)
async def refresh(
        _request: Request,
        payload: RefreshSchema,
        usecase: AbstractRefreshUseCase = Depends(refresh_use_case)
) -> JSONResponse:
    try:
        refresh_token = await usecase.execute(refresh_token=payload.refresh_token)
    except InvalidRefreshToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token = LoginResultSchema(
        access_token=refresh_token.access_token,
        refresh_token=refresh_token.refresh_token,
    )

    return JSONResponse(token.model_dump(mode="json"), status_code=status.HTTP_200_OK)


@router.post("/logout")
async def logout(
    payload: RefreshSchema,
    usecase: AbstractLogoutUseCase = Depends(logout_use_case),
) -> JSONResponse:
    await usecase.execute(refresh_token=payload.refresh_token)
    return JSONResponse({}, status_code=status.HTTP_204_NO_CONTENT)


def _to_schema(dto: AccountDTO):
    return AccountSchema(
        id=dto.id,
        email=dto.email,
        is_verified=dto.is_verified,
        verified_at=dto.verified_at,
    )