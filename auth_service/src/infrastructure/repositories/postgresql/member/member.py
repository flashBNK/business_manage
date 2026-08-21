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
        stmt = select(MemberModel).where((MemberModel.user_id == user_id), MemberModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        members = result.scalars().all()

        if not members:
            return []

        return [self._to_domain(member) for member in members]


    async def get_by_invite_id(self, invite_id: uuid.UUID) -> MemberDTO | None:
        stmt = select(MemberModel).where((MemberModel.invite_id == invite_id), MemberModel.is_active.is_(True))
        result = await self._session.execute(stmt)
        member = result.scalar_one_or_none()

        return member


    async def activation_shift(self, member_id: uuid.UUID, flag: bool) -> MemberDTO | None:
        stmt = select(MemberModel).where(MemberModel.id == member_id)
        result = await self._session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            return None

        if flag:
            member.is_active = True
        else:
            member.is_active = False

        await self._session.flush()

        return self._to_domain(member)



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