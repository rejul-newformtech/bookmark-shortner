from uuid import UUID

from sqlalchemy import update

from app.core.logger import get_logger
from app.db.session import AsyncSessionLocal
from app.models.bookmarks import Bookmark
from app.models.visits import Visit

logger = get_logger(__name__)


async def record_visit_background(bookmark_id: UUID) -> None:
    """Background task to record a visit event and increment the visit counter asynchronously."""
    try:
        async with AsyncSessionLocal() as session:
            # 1. Create a Visit record
            visit = Visit(bookmark_id=bookmark_id)
            session.add(visit)

            # 2. Increment bookmark visit_count atomically
            await session.execute(
                update(Bookmark)
                .where(Bookmark.id == bookmark_id)
                .values(visit_count=Bookmark.visit_count + 1)
            )

            await session.commit()
            logger.info("Recorded background visit for bookmark=%s", bookmark_id)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Error recording background visit for bookmark=%s: %s", bookmark_id, exc
        )
