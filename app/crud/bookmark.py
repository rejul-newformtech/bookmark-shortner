from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logger import get_logger
from app.crud.base import CRUDBase
from app.models.bookmarks import Bookmark

logger = get_logger(__name__)


class BookmarkService(CRUDBase[Bookmark]):
    model = Bookmark

    async def db_bookmark(
        self, db: AsyncSession, user_id: UUID, url: str, short_code: str
    ):
        existing_bookmark = await db.scalar(
            select(Bookmark).where(
                Bookmark.original_url == url,
                Bookmark.user_id == user_id,
            )
        )
        if existing_bookmark:
            logger.warning("Bookmark Already exist")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL already used",
            )

        return await self.create(
            db,
            original_url=url,
            short_code=short_code,
            user_id=user_id,
        )

    async def get_bookmarks(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ):
        # all bookmarks for a user with optional search and pagination
        query = select(Bookmark).where(Bookmark.user_id == user_id)
        if search:
            query = query.where(
                (Bookmark.original_url.ilike(f"%{search}%"))
                | (Bookmark.short_code.ilike(f"%{search}%"))
            )
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_bookmark_by_short_code(
        self, db: AsyncSession, short_code: str, user_id: UUID
    ):
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.short_code == short_code,
                Bookmark.user_id == user_id,
            )
        )
        return result.scalars().first()


bookmark_service = BookmarkService()
