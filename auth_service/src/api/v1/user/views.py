import uuid

from fastapi import APIRouter, Request, Depends, status, HTTPException
from fastapi.responses import JSONResponse


from api.v1.token_dependencies import get_current_token
from api.v1.user.models import UpdateUserSchema, UserSchema
from domain.token.models import TokenDTO
from domain.user.exceptions import UserNotFound
from domain.user.models import UserDTO, UpdateUserDTO
from usecases.profile.update_user.abstract import AbstractUpdateUserUseCase

from .dependencies import update_user_use_case

router = APIRouter()


@router.patch("/me", response_model=UserDTO)
async def update_user(
        _request: Request,
        payload: UpdateUserSchema,
        token: TokenDTO = Depends(get_current_token),
        usecase: AbstractUpdateUserUseCase = Depends(update_user_use_case),
) -> JSONResponse:

    if not token.subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)

    dto = UpdateUserDTO(first_name=payload.first_name, last_name=payload.last_name)

    try:
        user = await usecase.execute(dto=dto, user_id=token.subject)
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return JSONResponse(_to_schema(user).model_dump(mode="json"), status_code=status.HTTP_200_OK)


def _to_schema(dto: UserDTO) -> UserSchema:
    return UserSchema(
        id=dto.id,
        first_name=dto.first_name,
        last_name=dto.last_name,
        status=dto.status,
        created_at=dto.created_at,
    )