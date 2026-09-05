from abc import ABC, abstractmethod
from uuid import UUID

from domain.abstract import AbstractRepository

from .exceptions import InvalidRequestUsersPosition
from .models import (
    CreateUsersPositionDTO,
    EmployeePositionDTO,
    GetManagerPositionDTO,
    GetUsersPositionDTO,
    UpdateRoleUsersPositionDTO,
    UpdateUsersPositionDTO,
    UsersPositionDTO,
)


class AbstractUsersPositionRepository(AbstractRepository[UsersPositionDTO, UUID, CreateUsersPositionDTO], ABC):
    @abstractmethod
    async def delete_by_dto(self, dto: GetUsersPositionDTO) -> None:
        raise InvalidRequestUsersPosition

    @abstractmethod
    async def list_by_struct_adm(
        self, struct_adm_id: UUID, company_id: UUID, struct_adm_path: str, include_children: bool = False
    ) -> list[EmployeePositionDTO]:
        raise InvalidRequestUsersPosition

    @abstractmethod
    async def update(self, dto: UpdateUsersPositionDTO) -> UsersPositionDTO:
        raise InvalidRequestUsersPosition

    @abstractmethod
    async def update_role(self, dto: UpdateRoleUsersPositionDTO) -> UsersPositionDTO:
        raise InvalidRequestUsersPosition

    @abstractmethod
    async def get_manager(self, dto: GetManagerPositionDTO) -> UsersPositionDTO | None:
        raise InvalidRequestUsersPosition

    @abstractmethod
    async def list_by_position(self, company_id: UUID, position_id: UUID) -> list[EmployeePositionDTO]:
        raise InvalidRequestUsersPosition
