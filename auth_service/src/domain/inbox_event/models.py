from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class InboxEventDTO:
    event_id: UUID
    consumer_name: str
    processed_at: datetime


@dataclass(slots=True)
class CreateInboxEventDTO:
    event_id: UUID
    consumer_name: str
