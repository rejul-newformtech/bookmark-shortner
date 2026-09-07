from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class BookmarkSortBy(str, Enum):
    CREATED_AT = "created_at"
    VISIT_COUNT = "visit_count"
    ORIGINAL_URL = "original_url"
    SHORT_CODE = "short_code"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


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


class BookmarkBatchUploadResponse(BaseModel):
    message: str
    total_found: int
    created_count: int
    existing_count: int
    bookmarks: list[BookmarkResponse]
