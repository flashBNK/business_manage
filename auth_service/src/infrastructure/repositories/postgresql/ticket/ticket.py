import datetime
import uuid

from domain.ticket.exceptions import TicketNotFound, TooManyAttempts
from domain.ticket.models import CreateTicketDTO, TicketDTO
from domain.ticket.repository import AbstractTicketRepository
from infrastructure.databases.postgresql.models.ticket import Ticket as TicketModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLTicketRepository(AbstractTicketRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateTicketDTO) -> TicketDTO:
        stmt = select(TicketModel).where(TicketModel.email == dto.email)
        result = await self._session.execute(stmt)
        tickets = result.scalars().all()

        if tickets:
            for invite in tickets:
                await self.delete(invite.id)

        db_ticket = TicketModel(
            email=dto.email,
            code=dto.code,
            expires_at=dto.expires_at,
        )

        self._session.add(db_ticket)
        await self._session.flush()

        return self._to_domain(db_ticket)

    async def get_by_code(self, code: str) -> TicketDTO | None:
        query = select(TicketModel).where(TicketModel.code == code)
        result = await self._session.execute(query)
        ticket = result.scalar_one_or_none()

        if not ticket:
            return None

        return self._to_domain(ticket)

    async def update(self, ticket_id: uuid.UUID) -> TicketDTO:
        stmt = select(TicketModel).where(TicketModel.id == ticket_id)
        result = await self._session.execute(stmt)
        ticket = result.scalar_one_or_none()
        if not ticket:
            raise TicketNotFound

        ticket.attempts += 1
        if ticket.attempts >= 3:
            await self._session.delete(ticket)
            raise TooManyAttempts

        await self._session.flush()
        return self._to_domain(ticket)

    async def delete(self, ticket_id: uuid.UUID) -> None:
        stmt = select(TicketModel).where(TicketModel.id == ticket_id)
        result = await self._session.execute(stmt)
        ticket = result.scalar_one_or_none()

        if not ticket:
            raise TicketNotFound

        await self._session.delete(ticket)
        await self._session.flush()


    async def get(self, invite_id: uuid.UUID) -> TicketDTO | None:
        pass

    @staticmethod
    def _to_domain(invite: TicketModel) -> TicketDTO:
        return TicketDTO(
            id=invite.id,
            email=invite.email,
            code=invite.code,
            expires_at=invite.expires_at,
            attempts=invite.attempts,
            created_at=invite.created_at,
        )
