import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account.models import AccountDTO, CreateAccountDTO
from domain.account.repository import AbstractAccountRepository
from infrastructure.databases.postgresql.models.account import Account as AccountModel


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
        query = select(AccountModel).where((AccountModel.email == email))
        result = await self._session.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            return None

        return self._to_domain(account)


    async def delete(self, account_id: int) -> None:
        pass

    async def get(self, account_id: int) -> AccountDTO:
        pass


    @staticmethod
    def _to_domain(user: AccountModel) -> AccountDTO:
        return AccountDTO(
            id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            verified_at=user.verified_at,
        )