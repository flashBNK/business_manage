from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class StructAdmDTO:
    id: UUID
    company_id: UUID
    name: str
    path: str
    manager_id: UUID | None = None


@dataclass(slots=True)
class CreateStructAdmDTO:
    company_id: UUID
    name: str
    path: str | None = None
    manager_id: UUID | None = None
