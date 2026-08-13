import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.member.models import MemberDTO, CreateMemberDTO
from domain.member.repository import AbstractMemberRepository
from infrastructure.databases.postgresql.models.members import Members as MemberModel


class PostgreSQLMemberRepository(AbstractMemberRepository):
    def __init__(self, session: AsyncSession):
        self._session = session


    async def create(self, dto: CreateMemberDTO) -> MemberDTO:
        db_member = MemberModel(
            user_id=dto.user_id,
            company_id=dto.company_id,
            invite_id=dto.invite_id,
            role=dto.role,
        )

        self._session.add(db_member)
        await self._session.flush()

        return self._to_domain(db_member)


    async def get_by_user_id(self, user_id: uuid.UUID) -> list[MemberDTO] | None:
        query = select(MemberModel).where((MemberModel.user_id == user_id), MemberModel.is_active.is_(True))
        result = await self._session.execute(query)
        members = result.scalars().all()

        if not members:
            return []

        return [self._to_domain(member) for member in members]


    async def delete(self, account_id: int) -> None:
        pass

    async def get(self, account_id: int) -> MemberDTO:
        pass


    @staticmethod
    def _to_domain(member: MemberModel) -> MemberDTO:
        return MemberDTO(
            id=member.id,
            user_id=member.user_id,
            company_id=member.company_id,
            invite_id=member.invite_id,
            role=member.role,
            is_active=member.is_active,
        )