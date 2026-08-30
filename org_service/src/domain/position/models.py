from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CreatePositionDTO:
    name: str
    company_id: UUID
    description: str | None = None


@dataclass(slots=True)
class UpdatePositionDTO:
    name: str | None = None
    description: str | None = None


@dataclass(slots=True)
class PositionDTO:
    id: UUID
    company_id: UUID
    name: str
    description: str | None = None
