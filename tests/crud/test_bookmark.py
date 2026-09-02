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
    async def test_get_bookmarks_pagination_and_search(self, db_session):
        """Test getting bookmarks with pagination and search filtering."""
        user_id = uuid4()

        b1 = await bookmark_service.db_bookmark(
            db=db_session, user_id=user_id, url="https://python.org", short_code="py123"
        )
        b2 = await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user_id,
            url="https://fastapi.tiangolo.com",
            short_code="fa456",
        )
        b3 = await bookmark_service.db_bookmark(
            db=db_session, user_id=user_id, url="https://github.com", short_code="gh789"
        )

        # Test limit
        page1 = await bookmark_service.get_bookmarks(
            db=db_session, user_id=user_id, skip=0, limit=2
        )
        assert len(page1) == 2

        # Test skip
        page2 = await bookmark_service.get_bookmarks(
            db=db_session, user_id=user_id, skip=2, limit=2
        )
        assert len(page2) == 1

        # Assert deterministic ordering and page identity isolation
        all_created = sorted(
            [b1, b2, b3], key=lambda b: (b.created_at, b.id), reverse=True
        )
        page1_ids = [b.id for b in page1]
        page2_ids = [b.id for b in page2]
        assert page1_ids == [b.id for b in all_created[:2]]
        assert page2_ids == [b.id for b in all_created[2:]]
        assert set(page1_ids).isdisjoint(set(page2_ids))

        # Test search filter with case-insensitive URL
        search_res = await bookmark_service.get_bookmarks(
            db=db_session, user_id=user_id, search="FASTAPI"
        )
        assert len(search_res) == 1
        assert "fastapi" in search_res[0].original_url

        # Test search filter with mixed-case short_code
        short_code_res = await bookmark_service.get_bookmarks(
            db=db_session, user_id=user_id, search="FA456"
        )
        assert len(short_code_res) == 1
        assert short_code_res[0].id == b2.id

        # Test search filter with literal wildcard characters (% and _)
        b_special = await bookmark_service.db_bookmark(
            db=db_session,
            user_id=user_id,
            url="https://deals.com/100%_sale",
            short_code="sale_100",
        )
        special_res = await bookmark_service.get_bookmarks(
            db=db_session, user_id=user_id, search="100%"
        )
        assert len(special_res) == 1
        assert special_res[0].id == b_special.id

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
