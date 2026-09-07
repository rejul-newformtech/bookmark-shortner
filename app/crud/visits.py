from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.bookmarks import Bookmark
from app.models.visits import Visit
from app.schemas.visits import VisitCreate, Visited, VisitUpdate


class CRUDVisit(CRUDBase[Visit, VisitCreate, VisitUpdate]):
    async def visit(self, db: AsyncSession, visited: Visited) -> Visit:
        created = await self.create(db, bookmark_id=UUID(str(visited.bookmark_id)))
        await db.refresh(created, ["bookmark"])
        return created

    async def get_all(self, db: AsyncSession) -> list[Visit]:
        result = await db.execute(
            select(Visit)
            .options(selectinload(Visit.bookmark))
            .order_by(Visit.visited_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, object_id: Any) -> Visit | None:
        result = await db.execute(
            select(Visit)
            .options(selectinload(Visit.bookmark))
            .where(Visit.id == object_id)
        )
        return result.scalar_one_or_none()

    async def get_by_bookmark_id(
        self, db: AsyncSession, bookmark_id: UUID
    ) -> list[Visit]:
        result = await db.execute(
            select(Visit)
            .options(selectinload(Visit.bookmark))
            .where(Visit.bookmark_id == bookmark_id)
            .order_by(Visit.visited_at.desc())
        )
        return list(result.scalars().all())

    async def get_site_by_bookmark_id(
        self, db: AsyncSession, bookmark_id: UUID, user_id: UUID | None = None
    ) -> Bookmark | None:
        query = select(Bookmark).where(Bookmark.id == bookmark_id)
        if user_id is not None:
            query = query.where(Bookmark.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()


visit = CRUDVisit(Visit)
