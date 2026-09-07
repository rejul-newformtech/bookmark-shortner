from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.bookmark import BookmarkResponse


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
    bookmark: BookmarkResponse | None = None

    model_config = {"from_attributes": True}


class BookmarkVisitsResponse(BaseModel):
    bookmark: BookmarkResponse
    visits: list[VisitResponse]

    model_config = {"from_attributes": True}


# Alias for backward compatibility if referenced
BookmarkSiteVisitsResponse = BookmarkVisitsResponse
