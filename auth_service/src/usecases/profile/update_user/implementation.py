import uuid

from domain.token.repository import AbstractTokenService
from domain.user.models import UpdateUserDTO, UserDTO
from infrastructure.repositories.postgresql.uow import PostgreSQLUnitOfWork
from logger import get_logger

from .abstract import AbstractUpdateUserUseCase

log = get_logger(__name__)


class PostgreSQLUpdateUserUseCase(AbstractUpdateUserUseCase):
    def __init__(self, uow: PostgreSQLUnitOfWork, token_service: AbstractTokenService):
        self._uow = uow
        self._token_service = token_service

    async def execute(self, dto: UpdateUserDTO, user_id: uuid.UUID) -> UserDTO:
        async with self._uow as uow:
            user = await uow.user.update(user_id=user_id, dto=dto)
            return user
