import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.bookmarks import Bookmark


def generate_short_code(length: int = 10) -> str:
    """Generate a random short code of specified length."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


async def create_unique_short_code(db: AsyncSession) -> str:
    """Generate a unique short code that doesn't exist in the database."""
    short_code = generate_short_code()
    result = await db.execute(
        select(Bookmark).filter(Bookmark.short_code == short_code)
    )
    existing_bookmark = result.scalars().first()

    while existing_bookmark:
        short_code = generate_short_code()
        result = await db.execute(
            select(Bookmark).filter(Bookmark.short_code == short_code)
        )
        existing_bookmark = result.scalars().first()
    return short_code
