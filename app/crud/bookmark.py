from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.crud.base import CRUDBase
from app.models.bookmarks import Bookmark
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate

logger = get_logger(__name__)


class CRUDBookmark(CRUDBase[Bookmark, BookmarkCreate, BookmarkUpdate]):
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
        sort_by: str = "created_at",
        order: str = "desc",
    ):
        # all bookmarks for a user with optional search, pagination, and sorting
        query = select(Bookmark).where(Bookmark.user_id == user_id)
        if search:
            escaped_search = (
                search.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
            )
            pattern = f"%{escaped_search}%"
            query = query.where(
                Bookmark.original_url.ilike(pattern, escape="\\")
                | Bookmark.short_code.ilike(pattern, escape="\\")
            )

        sort_column_map = {
            "created_at": Bookmark.created_at,
            "date": Bookmark.created_at,
            "visit_count": Bookmark.visit_count,
            "visits": Bookmark.visit_count,
            "original_url": Bookmark.original_url,
            "url": Bookmark.original_url,
            "short_code": Bookmark.short_code,
        }
        sort_column = sort_column_map.get(sort_by, Bookmark.created_at)

        if order.lower() == "asc":
            order_clause = (sort_column.asc(), Bookmark.id.asc())
        else:
            order_clause = (sort_column.desc(), Bookmark.id.desc())

        query = query.order_by(*order_clause).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

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

    async def get_by_url_and_user(
        self, db: AsyncSession, user_id: UUID, url: str
    ) -> Bookmark | None:
        return await db.scalar(
            select(Bookmark).where(
                Bookmark.original_url == url,
                Bookmark.user_id == user_id,
            )
        )

    async def batch_process_pdf_urls(
        self, db: AsyncSession, user_id: UUID, urls: list[str]
    ) -> tuple[list[Bookmark], int, int]:
        from app.utils.shortner import create_unique_short_code

        if not urls:
            return [], 0, 0

        # Bulk fetch all existing bookmarks for this user in one query
        result = await db.execute(
            select(Bookmark).where(
                Bookmark.user_id == user_id,
                Bookmark.original_url.in_(urls),
            )
        )
        existing_map: dict[str, Bookmark] = {
            str(b.original_url): b for b in result.scalars().all()
        }

        bookmarks: list[Bookmark] = []
        new_bookmarks: list[Bookmark] = []
        created_count = 0
        existing_count = 0
        allocated_short_codes: set[str] = set()

        for url in urls:
            if url in existing_map:
                bookmarks.append(existing_map[url])
                existing_count += 1
            else:
                while True:
                    short_code = await create_unique_short_code(db)
                    if short_code not in allocated_short_codes:
                        allocated_short_codes.add(short_code)
                        break

                new_bm = Bookmark(
                    original_url=url,
                    short_code=short_code,
                    user_id=user_id,
                )
                existing_map[url] = new_bm
                new_bookmarks.append(new_bm)
                bookmarks.append(new_bm)
                created_count += 1

        # Stage and persist all new bookmarks in a single atomic transaction
        if new_bookmarks:
            db.add_all(new_bookmarks)
            await db.commit()
            for b in new_bookmarks:
                await db.refresh(b)

        return bookmarks, created_count, existing_count


bookmark = CRUDBookmark(Bookmark)
