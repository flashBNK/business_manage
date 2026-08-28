from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CompanyReplicaDTO:
    id: UUID
    name: str


@dataclass(slots=True)
class CreateCompanyReplicaDTO:
    name: str
    company_id: UUID | None = None
