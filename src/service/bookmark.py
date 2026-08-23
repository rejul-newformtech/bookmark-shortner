from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.bookmarks import Bookmark


class BookmarkService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def db_bookmark(self, user_id: UUID, url: str, short_code: str):
        existing_bookmark = await self.db.scalar(
            select(Bookmark).where(
                Bookmark.original_url == url,
                Bookmark.user_id == user_id,
            )
        )
        if existing_bookmark:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL already used",
            )

        result = Bookmark(original_url=url, short_code=short_code, user_id=user_id)
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_bookmarks(self, user_id: UUID):
        # all bookmarks for a user
        result = await self.db.execute(
            select(Bookmark).where(Bookmark.user_id == user_id)
        )
        return result.scalars().all()

    async def get_bookmark_by_short_code(self, short_code: str, user_id: UUID):
        result = await self.db.execute(
            select(Bookmark).where(
                Bookmark.short_code == short_code,
                Bookmark.user_id == user_id,
            )
        )
        return result.scalars().first()
