from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Visit(BaseModel):
    pass


class Visited(Visit):
    bookmark_id: UUID


class VisitResponse(BaseModel):
    id: UUID
    bookmark_id: UUID
    visited_at: datetime

    model_config = {"from_attributes": True}
