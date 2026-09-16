from datetime import UTC, datetime
from uuid import UUID, uuid4

from infrastructure.databases.postgresql.models import (
    CompanyReplica,
    Position,
    StructAdm,
    StructAdmPosition,
    UsersPosition,
    UsersReplica,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import Ltree


async def create_company(
    session: AsyncSession, company_id: UUID | None = None, name: str = "Test Company"
) -> CompanyReplica:
    company = CompanyReplica(id=company_id or uuid4(), name=name)

    session.add(company)
    await session.commit()

    return company


async def create_root_structure(session: AsyncSession, company_id: UUID, name: str = "Root") -> StructAdm:
    root = StructAdm(id=uuid4(), company_id=company_id, name=name, path=Ltree(f"c{company_id.hex}"))

    session.add(root)
    await session.commit()

    return root


async def create_user(
    session: AsyncSession,
    user_id: UUID | None = None,
    company_id: UUID | None = None,
    username: str = "Ivan Ivanov",
) -> UsersReplica:
    user = UsersReplica(
        id=user_id or uuid4(),
        username=username,
        company_id=company_id or uuid4(),
        is_active=True,
        last_event_at=datetime.now(UTC),
    )

    session.add(user)
    await session.commit()

    return user


async def create_position(
    session: AsyncSession,
    company_id: UUID,
    position_id: UUID | None = None,
    name: str = "Backend Developer",
    description: str | None = None,
) -> Position:
    position = Position(id=position_id or uuid4(), company_id=company_id, name=name, description=description)

    session.add(position)
    await session.commit()

    return position


async def create_struct_adm_position(
    session: AsyncSession, struct_adm_id: UUID, position_id: UUID
) -> StructAdmPosition:
    relation = StructAdmPosition(struct_adm_id=struct_adm_id, position_id=position_id)

    session.add(relation)
    await session.commit()

    return relation


async def create_users_position(
    session: AsyncSession, user_id: UUID, struct_adm_id: UUID, position_id: UUID, role: str = "member"
) -> UsersPosition:
    users_position = UsersPosition(user_id=user_id, struct_adm_id=struct_adm_id, position_id=position_id, role=role)

    session.add(users_position)
    await session.commit()

    return users_position
