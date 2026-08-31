"""Test cases for bookmark CRUD operations."""

from uuid import uuid4

import pytest

from app.crud.bookmark import bookmark_service


class TestBookmarkCRUD:
    """Test bookmark CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_bookmark(self, db_session):
        """Test creating a bookmark."""
        user_id = uuid4()

        bookmark = await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user_id,
            url="https://www.example.com",
            short_code="abc123",
        )

        assert "example.com" in str(bookmark.original_url)
        assert bookmark.short_code == "abc123"
        assert bookmark.user_id == user_id
        assert bookmark.visit_count == 0

    @pytest.mark.asyncio
    async def test_get_bookmarks_by_user(self, db_session):
        """Test getting bookmarks for a user."""
        user_id = uuid4()

        # Create multiple bookmarks
        urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
        ]

        for i, url in enumerate(urls):
            await bookmark_service.db_bookmark(
                db=db_session,
                user_id=user_id,
                url=url,
                short_code=f"code{i}",
            )

        # Get bookmarks
        bookmarks = await bookmark_service.get_bookmarks(db=db_session, user_id=user_id)

        assert len(bookmarks) == 3
        assert all(b.user_id == user_id for b in bookmarks)

    @pytest.mark.asyncio
    async def test_get_empty_bookmarks_for_user(self, db_session):
        """Test getting bookmarks for user with no bookmarks."""
        user_id = uuid4()

        bookmarks = await bookmark_service.get_bookmarks(db=db_session, user_id=user_id)

        assert bookmarks == []

    @pytest.mark.asyncio
    async def test_get_bookmark_by_short_code(self, db_session):
        """Test getting bookmark by short code."""
        user_id = uuid4()

        created = await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user_id,
            url="https://www.example.com",
            short_code="mycode",
        )

        retrieved = await bookmark_service.get_bookmark_by_short_code(
            db=db_session, short_code="mycode", user_id=user_id
        )

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.short_code == "mycode"

    @pytest.mark.asyncio
    async def test_get_bookmark_wrong_user(self, db_session):
        """Test that user cannot get another user's bookmark."""
        user1_id = uuid4()
        user2_id = uuid4()

        # Create bookmark for user 1
        await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user1_id,
            url="https://www.example.com",
            short_code="usercode",
        )

        # Try to get as user 2
        retrieved = await bookmark_service.get_bookmark_by_short_code(
            db=db_session, short_code="usercode", user_id=user2_id
        )

        # Should return None, not raise exception
        assert retrieved is None


class TestBookmarkDeletion:
    """Test bookmark deletion."""

    @pytest.mark.asyncio
    async def test_delete_bookmark(self, db_session):
        """Test deleting a bookmark."""
        user_id = uuid4()

        bookmark = await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user_id,
            url="https://www.example.com",
            short_code="todelpete",
        )

        result = await bookmark_service.delete(db=db_session, object_id=bookmark.id)

        assert result is True

        # Verify it's deleted
        remaining = await bookmark_service.get_bookmarks(db=db_session, user_id=user_id)
        assert len(remaining) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_bookmark(self, db_session):
        """Test deleting non-existent bookmark returns False."""
        fake_id = uuid4()

        result = await bookmark_service.delete(db=db_session, object_id=fake_id)

        assert result is False
