import uuid

from domain.user.exceptions import UserNotFound
from domain.user.models import CreateUserDTO, UpdateUserDTO, UserDTO
from domain.user.repository import AbstractUserRepository
from infrastructure.databases.postgresql.models.user import User as UserModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateUserDTO) -> UserDTO:
        db_user = UserModel(first_name=dto.first_name, last_name=dto.last_name)
        self._session.add(db_user)
        await self._session.flush()
        return self._to_domain(db_user)

    async def update(self, dto: UpdateUserDTO, user_id: uuid.UUID) -> UserDTO:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFound

        if dto.first_name:
            user.first_name = dto.first_name
        if dto.last_name:
            user.last_name = dto.last_name

        self._session.add(user)
        await self._session.flush()

        return self._to_domain(user)

    async def get(self, user_id: uuid.UUID) -> UserDTO:
        pass

    async def delete(self, user_id: uuid.UUID) -> None:
        pass

    @staticmethod
    def _to_domain(user: UserModel) -> UserDTO:
        return UserDTO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            created_at=user.created_at,
        )
