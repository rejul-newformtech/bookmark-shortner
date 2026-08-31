"""Test cases for analytics background services."""

from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.bookmarks import Bookmark
from app.models.users import User
from app.models.visits import Visit
from app.service.analytics import record_visit_background


class TestAnalyticsService:
    """Test background analytics tracking."""

    @pytest.mark.asyncio
    async def test_record_visit_background(self, db_session):
        """Test recording a visit event in the background."""
        user = User(
            id=uuid4(),
            username="analytictester",
            email="analytics@example.com",
            hashed_password="hashed_pass_sample",
        )
        db_session.add(user)
        await db_session.commit()

        bookmark = Bookmark(
            id=uuid4(),
            user_id=user.id,
            original_url="https://www.example.com",
            short_code="bgtest1",
            visit_count=0,
        )
        db_session.add(bookmark)
        await db_session.commit()

        # Run background task
        await record_visit_background(bookmark.id)

        # Verify visit record was created and visit_count was incremented
        visit_count = await db_session.scalar(
            select(Bookmark.visit_count).where(Bookmark.id == bookmark.id)
        )
        assert visit_count == 1

        visit_id = await db_session.scalar(
            select(Visit.id).where(Visit.bookmark_id == bookmark.id)
        )
        assert visit_id is not None
