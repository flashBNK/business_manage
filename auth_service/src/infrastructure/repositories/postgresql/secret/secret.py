import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.secret.exceptions import SecretNotFound, WrongSecretPassword
from domain.secret.models import SecretDTO, CreateSecretDTO
from domain.secret.repository import AbstractSecretRepository
from domain.secret.crypto import context
from infrastructure.databases.postgresql.models.secret import Secret as SecretModel


class PostgreSQLSecretRepository(AbstractSecretRepository):
    def __init__(self, session: AsyncSession):
        self._session = session


    async def create(self, dto: CreateSecretDTO) -> SecretDTO:
        db_secret = SecretModel(
            user_id=dto.user_id,
            account_id=dto.account_id,
            password_hash=context.hash(dto.password),
        )

        self._session.add(db_secret)
        await self._session.flush()

        return self._to_domain(db_secret)


    async def delete(self, secret_id: uuid.UUID) -> None:
        stmt = select(SecretModel).where(SecretModel.id == secret_id)
        result = await self._session.execute(stmt)
        secret = result.scalar_one_or_none()

        if not secret:
            raise SecretNotFound

        await self._session.delete(secret)
        await self._session.flush()


    async def get(self, secret_id: uuid.UUID) -> SecretDTO:
        pass

    async def check_and_get_by_account_id(self, account_id: int, password: str) -> SecretDTO:
        stmt = select(SecretModel).where(SecretModel.account_id == account_id)
        result = await self._session.execute(stmt)
        secret = result.scalar_one_or_none()

        if not secret:
            raise SecretNotFound

        if not context.verify(password, secret.password_hash):
            raise WrongSecretPassword

        return self._to_domain(secret)


    async def get_by_account_id(self, account_id: uuid.UUID) -> SecretDTO | None:
        stmt = select(SecretModel).where(SecretModel.account_id == account_id)
        result = await self._session.execute(stmt)
        secret = result.scalar_one_or_none()

        if not secret:
            return None

        return self._to_domain(secret)


    async def list_by_user_id(self, user_id: uuid.UUID) -> list[SecretDTO]:
        stmt = select(SecretModel).where(SecretModel.user_id == user_id)
        result = await self._session.execute(stmt)
        secrets = result.scalars().all()

        if not secrets:
            return []

        return [self._to_domain(secret=secret) for secret in secrets]


    @staticmethod
    def _to_domain(secret: SecretModel) -> SecretDTO:
        return SecretDTO(
            id=secret.id,
            user_id=secret.user_id,
            account_id=secret.account_id,
        )