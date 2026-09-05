from uuid import UUID

from domain.struct_adm.exceptions import NodeHasDependentsException, NodeHasRootStructAdm
from domain.struct_adm.models import (
    CreateStructAdmDTO,
    StructAdmDTO,
    UpdateStructAdmDTO,
)
from domain.struct_adm.repository import AbstractStructAdmRepository
from infrastructure.databases.postgresql.models.struct_adm import StructAdm as StructAdmModel
from logger import get_logger
from sqlalchemy import String, bindparam, case, cast, func, literal, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import UserDefinedType
from sqlalchemy_utils import Ltree, LtreeType

log = get_logger(__name__)


class LtreeSQLType(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kwargs) -> str:
        return "LTREE"


class PostgreSQLStructAdmRepository(AbstractStructAdmRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        db_struct_adm = StructAdmModel(
            id=dto.id,
            company_id=dto.company_id,
            name=dto.name,
            path=Ltree(dto.path),
        )

        self._session.add(db_struct_adm)
        await self._session.flush()

        return self._to_domain(db_struct_adm)

    async def ensure_root(self, dto: CreateStructAdmDTO) -> StructAdmDTO:
        path = Ltree(f"c{dto.company_id.hex}")

        stmt = (
            insert(StructAdmModel)
            .values(company_id=dto.company_id, name=dto.name, path=path)
            .on_conflict_do_update(index_elements=["path"], set_={"name": dto.name})
            .returning(StructAdmModel)
        )

        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one()

        return self._to_domain(struct_adm)

    async def delete(self, struct_adm_id: UUID) -> None:
        stmt = select(StructAdmModel).where(StructAdmModel.id == struct_adm_id)
        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one_or_none()

        if not struct_adm:
            return None

        current_level = len(str(struct_adm.path).split("."))
        if current_level == 1:
            raise NodeHasRootStructAdm

        path_param = bindparam("path", type_=String())
        path_expr = cast(path_param, LtreeSQLType())

        stmt = (
            select(StructAdmModel.id)
            .where(
                StructAdmModel.path.op("<@")(path_expr),
                func.nlevel(StructAdmModel.path) == current_level + 1,
            )
            .limit(1)
        )

        descendants = await self._session.scalar(stmt, {"path": str(struct_adm.path)})

        if descendants:
            raise NodeHasDependentsException

        await self._session.delete(struct_adm)
        await self._session.flush()

    async def get(self, struct_adm_id: UUID) -> StructAdmDTO | None:
        stmt = select(StructAdmModel).where(StructAdmModel.id == struct_adm_id)
        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one_or_none()

        if not struct_adm:
            return None

        return self._to_domain(struct_adm)

    async def get_children(self, parent_path: str) -> list[StructAdmDTO]:
        parent_level = len(parent_path.split("."))

        parent_path_expr = cast(literal(parent_path), LtreeType())

        stmt = (
            select(StructAdmModel)
            .where(
                StructAdmModel.path.op("<@")(parent_path_expr),
                func.nlevel(StructAdmModel.path) == parent_level + 1,
            )
            .order_by(StructAdmModel.path)
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(struct_adm) for struct_adm in result.scalars()]

    async def get_descendants(self, parent_path: str) -> list[StructAdmDTO]:
        parent_path_expr = cast(literal(parent_path), LtreeType())

        stmt = (
            select(StructAdmModel)
            .where(
                StructAdmModel.path.op("<@")(parent_path_expr),
            )
            .order_by(StructAdmModel.path)
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(struct_adm) for struct_adm in result.scalars()]

    async def get_ancestors(self, struct_adm_path: str) -> list[StructAdmDTO]:
        struct_adm_path_expr = cast(literal(struct_adm_path), LtreeType())

        stmt = (
            select(StructAdmModel)
            .where(
                StructAdmModel.path.op("@>")(struct_adm_path_expr),
            )
            .order_by(StructAdmModel.path)
        )

        result = await self._session.execute(stmt)

        return [self._to_domain(struct_adm) for struct_adm in result.scalars()]

    async def update(self, struct_adm_id: UUID, dto: UpdateStructAdmDTO) -> StructAdmDTO:
        stmt = select(StructAdmModel).where(StructAdmModel.id == struct_adm_id)
        result = await self._session.execute(stmt)
        struct_adm = result.scalar_one_or_none()

        if dto.name:
            struct_adm.name = dto.name
        self._session.add(struct_adm)
        await self._session.flush()

        return self._to_domain(struct_adm)

    async def move_subtree(self, old_path: str, new_path: str) -> None:
        old_path_expr = cast(literal(old_path), LtreeType())
        new_path_expr = cast(literal(new_path), LtreeType())

        old_level = func.nlevel(old_path_expr)
        descendant_path = new_path_expr.op("||")(func.subpath(StructAdmModel.path, old_level))

        new_struct_adm_path = case((StructAdmModel.path == old_path_expr, new_path_expr), else_=descendant_path)

        stmt = (
            update(StructAdmModel).where(StructAdmModel.path.op("<@")(old_path_expr)).values(path=new_struct_adm_path)
        )

        await self._session.execute(stmt)

    async def list_tree(self, company_id: UUID) -> list[StructAdmDTO]:
        stmt = select(StructAdmModel).where(StructAdmModel.company_id == company_id).order_by(StructAdmModel.path)
        result = await self._session.execute(stmt)
        struct_adms = result.scalars().all()

        return [self._to_domain(struct_adm) for struct_adm in struct_adms]

    @staticmethod
    def _to_domain(struct_adm: StructAdmModel) -> StructAdmDTO:
        return StructAdmDTO(
            id=struct_adm.id,
            company_id=struct_adm.company_id,
            name=struct_adm.name,
            path=str(struct_adm.path),
        )
