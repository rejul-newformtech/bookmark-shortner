from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Visit(BaseModel):
    pass


class VisitCreate(BaseModel):
    bookmark_id: UUID


class VisitUpdate(BaseModel):
    bookmark_id: UUID | None = None


class Visited(VisitCreate):
    pass


class VisitResponse(BaseModel):
    id: UUID
    bookmark_id: UUID
    visited_at: datetime

    model_config = {"from_attributes": True}
