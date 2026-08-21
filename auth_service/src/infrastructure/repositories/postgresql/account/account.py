import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account.models import AccountDTO, CreateAccountDTO, UpdateAccountDTO
from domain.account.repository import AbstractAccountRepository
from infrastructure.databases.postgresql.models.account import Account as AccountModel
from infrastructure.databases.postgresql.models.secret import Secret as SecretModel


class PostgreSQLAccountRepository(AbstractAccountRepository):
    def __init__(self, session: AsyncSession):
        self._session = session


    async def create(self, dto: CreateAccountDTO) -> AccountDTO:
        db_account = AccountModel(
            email=dto.email,
            is_verified=True,
            verified_at=datetime.datetime.now(datetime.UTC),
        )

        self._session.add(db_account)
        await self._session.flush()

        return self._to_domain(db_account)


    async def get_by_email(self, email: str) -> AccountDTO | None:
        stmt = select(AccountModel).where((AccountModel.email == email))
        result = await self._session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            return None

        return self._to_domain(account)


    async def list_by_user_id(self, user_id: int) -> tuple[list[AccountDTO], int]:
        count_stmt = select(func.count()).where(SecretModel.user_id == user_id)
        total = (await self._session.execute(count_stmt)).scalar()

        stmt = (
            select(AccountModel)
            .join(SecretModel, SecretModel.account_id == AccountModel.id)
            .where(SecretModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        accounts = result.scalars().all()

        if not accounts:
            return [], 0

        return [self._to_domain(account) for account in accounts], total


    async def delete(self, account_id: int) -> None:
        pass

    async def get(self, account_id: int) -> AccountDTO | None:
        stmt = select(AccountModel).where((AccountModel.id == account_id))
        result = await self._session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            return None

        return self._to_domain(account)

    async def update(self, dto: UpdateAccountDTO, account_id: int) -> AccountDTO | None:
        stmt = select(AccountModel).where((AccountModel.id == account_id))
        result = await self._session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            return None

        account.email = dto.email
        self._session.add(account)
        await self._session.flush()

        return self._to_domain(account)


    @staticmethod
    def _to_domain(user: AccountModel) -> AccountDTO:
        return AccountDTO(
            id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            verified_at=user.verified_at,
        )