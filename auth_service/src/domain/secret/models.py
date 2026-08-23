import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class CreateSecretDTO:
    account_id: uuid.UUID
    user_id: uuid.UUID
    password: str


@dataclass(slots=True)
class SecretDTO:
    id: uuid.UUID
    account_id: uuid.UUID
    user_id: uuid.UUID
