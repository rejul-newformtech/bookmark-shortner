"""Test cases for bookmark schemas."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.bookmark import BookmarkCreate, BookmarkResponse


class TestBookmarkCreateSchema:
    """Test BookmarkCreate schema validation."""

    def test_valid_bookmark_create(self):
        """Test creating valid bookmark."""
        bookmark_data = {"original_url": "https://www.example.com"}
        bookmark = BookmarkCreate(**bookmark_data)
        assert "example.com" in str(bookmark.original_url)

    def test_bookmark_url_validation(self):
        """Test bookmark URL validation."""
        bookmark_data = {"original_url": "not-a-valid-url"}
        with pytest.raises(ValidationError) as exc_info:
            BookmarkCreate(**bookmark_data)
        assert "valid URL" in str(exc_info.value)

    def test_bookmark_empty_url(self):
        """Test bookmark with empty URL."""
        bookmark_data = {"original_url": ""}
        with pytest.raises(ValidationError):
            BookmarkCreate(**bookmark_data)

    def test_bookmark_http_url(self):
        """Test bookmark with HTTP URL."""
        bookmark_data = {"original_url": "http://www.example.com"}
        bookmark = BookmarkCreate(**bookmark_data)
        assert "http" in str(bookmark.original_url)

    def test_bookmark_complex_url(self):
        """Test bookmark with complex URL."""
        bookmark_data = {
            "original_url": "https://www.example.com/path?query=value&other=123#anchor"
        }
        bookmark = BookmarkCreate(**bookmark_data)
        assert bookmark.original_url is not None


class TestBookmarkResponseSchema:
    """Test BookmarkResponse schema."""

    def test_bookmark_response_creation(self):
        """Test creating BookmarkResponse."""
        bookmark_dict = {
            "id": uuid4(),
            "original_url": "https://www.example.com",
            "short_code": "abc123",
            "visit_count": 5,
            "created_at": datetime.now(tz=UTC),
            "user_id": uuid4(),
        }
        bookmark = BookmarkResponse(**bookmark_dict)
        assert "example.com" in str(bookmark.original_url)
        assert bookmark.visit_count == 5

    def test_bookmark_response_requires_user_id(self):
        """Test that BookmarkResponse requires user_id."""
        bookmark_dict = {
            "id": uuid4(),
            "original_url": "https://www.example.com",
            "short_code": "abc123",
            "visit_count": 5,
            "created_at": datetime.now(tz=UTC),
            # Missing user_id
        }
        with pytest.raises(ValidationError) as exc_info:
            BookmarkResponse(**bookmark_dict)
        assert "user_id" in str(exc_info.value)
