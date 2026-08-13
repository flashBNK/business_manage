import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CompanyDTO:
    id: uuid.UUID
    name: str
    is_active: bool
    created_at: datetime


@dataclass(slots=True)
class CreateCompanyDTO:
    name: str