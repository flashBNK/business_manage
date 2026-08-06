import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.invite.exceptions import InviteNotFound
from domain.invite.models import InviteDTO, CreateInviteDTO, UpdateInviteDTO
from domain.invite.repository import AbstractInviteRepository
from infrastructure.databases.postgresql.models.invite import Invite as InviteModel


class PostgreSQLInviteRepository(AbstractInviteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session


    async def create(self, dto: CreateInviteDTO) -> InviteDTO:
        stmt = select(InviteModel).where(InviteModel.email == dto.email)
        result = await self._session.execute(stmt)
        invites = result.scalars().all()

        if invites:
            for invite in invites:
                await self.delete(invite.id)

        db_invite = InviteModel(
            email=dto.email,
            code=dto.code,
            expires_at=dto.expires_at
        )


        self._session.add(db_invite)
        await self._session.flush()

        return self._to_domain(db_invite)


    async def get_by_email(self, email: str) -> InviteDTO | None:
        query = select(InviteModel).where((InviteModel.email == email))
        result = await self._session.execute(query)
        invite = result.scalar_one_or_none()

        if not invite:
            return None

        return self._to_domain(invite)


    async def update(self, invite_id: uuid.UUID, dto: UpdateInviteDTO) -> InviteDTO:
        stmt = select(InviteModel).where(InviteModel.id == invite_id)
        result = await self._session.execute(stmt)
        invite = result.scalar_one_or_none()
        if not invite:
            raise InviteNotFound

        if dto.attempts is not None:
            invite.attempts = dto.attempts

        await self._session.flush()

        return self._to_domain(invite)


    async def delete(self, invite_id: uuid.UUID) -> None:
        stmt = select(InviteModel).where(InviteModel.id == invite_id)
        result = await self._session.execute(stmt)
        invite = result.scalar_one_or_none()

        if not invite:
            raise InviteNotFound()

        await self._session.delete(invite)
        await self._session.flush()


    async def get(self, invite_id: uuid.UUID) -> InviteDTO:
        pass


    @staticmethod
    def _to_domain(invite: InviteModel) -> InviteDTO:
        return InviteDTO(
            id=invite.id,
            email=invite.email,
            code=invite.code,
            expires_at=invite.expires_at,
            status=invite.status,
            attempts=invite.attempts,
            accepted_at=invite.accepted_at,
        )