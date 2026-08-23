import uuid

from domain.company.models import CompanyDTO, CreateCompanyDTO
from domain.company.repository import AbstractCompanyRepository
from infrastructure.databases.postgresql.models.company import Company as CompanyModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLCompanyRepository(AbstractCompanyRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, company_dto: CreateCompanyDTO) -> CompanyDTO:
        db_company = CompanyModel(name=company_dto.name)
        self._session.add(db_company)
        await self._session.flush()
        return self._to_domain(db_company)

    async def get(self, company_id: uuid.UUID) -> CompanyDTO:
        pass

    async def delete(self, company_id: uuid.UUID) -> None:
        pass

    async def get_by_name(self, company_dto: CreateCompanyDTO) -> CompanyDTO | None:
        stmt = select(CompanyModel).where(CompanyModel.name == company_dto.name)
        result = await self._session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            return None

        return self._to_domain(company)

    @staticmethod
    def _to_domain(company: CompanyModel) -> CompanyDTO:
        return CompanyDTO(
            id=company.id,
            name=company.name,
            is_active=company.is_active,
            created_at=company.created_at,
        )
