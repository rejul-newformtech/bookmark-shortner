"""Test cases for shortener utility functions."""

from uuid import uuid4

import pytest

from app.models.bookmarks import Bookmark
from app.utils.shortner import create_unique_short_code


class TestShortCodeGeneration:
    """Test short code generation for bookmarks."""

    @pytest.mark.asyncio
    async def test_short_code_generation(self, db_session):
        """Test generating short code."""
        short_code = await create_unique_short_code(db_session)

        assert isinstance(short_code, str)
        assert len(short_code) > 0
        assert len(short_code) <= 10

    @pytest.mark.asyncio
    async def test_short_code_uniqueness(self, db_session):
        """Test that generated short codes are unique."""
        short_codes = set()

        # Generate multiple short codes
        for _ in range(5):
            short_code = await create_unique_short_code(db_session)
            short_codes.add(short_code)

        # All should be unique
        assert len(short_codes) == 5

    @pytest.mark.asyncio
    async def test_short_code_format(self, db_session):
        """Test short code format."""
        short_code = await create_unique_short_code(db_session)

        # Should contain only alphanumeric characters
        assert short_code.isalnum()

    @pytest.mark.asyncio
    async def test_short_code_no_duplicates_in_db(self, db_session):
        """Test that generated short codes don't duplicate existing ones."""
        # Create a bookmark with a short code
        bookmark = Bookmark(
            id=uuid4(),
            user_id=uuid4(),
            original_url="https://www.example.com",
            short_code="abc123",
            visit_count=0,
        )
        db_session.add(bookmark)
        await db_session.commit()

        # Generate new short code - should not be "abc123"
        for _ in range(10):
            new_code = await create_unique_short_code(db_session)
            assert new_code != "abc123"
