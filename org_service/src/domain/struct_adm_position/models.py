from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CreateStructAdmPositionDTO:
    struct_adm_id: UUID
    position_id: UUID


@dataclass(slots=True)
class StructAdmPositionDTO(CreateStructAdmPositionDTO):
    pass
