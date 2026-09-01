from dataclasses import dataclass, field
from uuid import UUID, uuid4

from infrastructure.databases.postgresql.models.users_position import Role


@dataclass(slots=True)
class StructAdmDTO:
    id: UUID
    company_id: UUID
    name: str
    path: str | None = None
    manager_id: UUID | None = None


@dataclass(slots=True)
class UpdateStructAdmDTO:
    name: str
    manager_id: UUID | None = None


@dataclass(slots=True)
class MoveStructAdmDTO:
    new_parent_id: UUID


@dataclass(slots=True)
class CreateStructAdmDTO:
    company_id: UUID
    name: str
    id: UUID = field(default_factory=uuid4)
    path: str | None = None
    manager_id: UUID | None = None


@dataclass(slots=True)
class AddManagerStructAdmDTO:
    user_id: UUID
    struct_adm_id: UUID
    position_id: UUID


@dataclass(slots=True)
class DeleteManagerStructAdmDTO(AddManagerStructAdmDTO):
    pass


@dataclass(slots=True)
class ManagerDTO(AddManagerStructAdmDTO):
    role: Role


@dataclass(slots=True)
class CompanyStructureDTO:
    id: UUID
    name: str
    manager_id: UUID | None = None
    children: list["StructAdmTreeDTO"] = field(default_factory=list)


@dataclass(slots=True)
class StructAdmTreeDTO:
    id: UUID
    name: str
    path: str
    manager_id: UUID | None = None
    children: list["StructAdmTreeDTO"] = field(default_factory=list)
