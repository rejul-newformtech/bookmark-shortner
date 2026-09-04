from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class BookmarkBase(BaseModel):
    original_url: HttpUrl


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    original_url: HttpUrl | None = None


class BookmarkResponse(BookmarkBase):
    id: UUID
    short_code: str
    visit_count: int
    created_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True
