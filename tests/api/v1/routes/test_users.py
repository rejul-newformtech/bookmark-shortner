"""Test cases for user profile endpoints."""

import pytest
from httpx import AsyncClient


class TestUserProfile:
    """Test user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_profile_by_username(
        self, client_with_auth: AsyncClient, test_user_data: dict
    ):
        """Test getting user profile by username."""
        response = await client_with_auth.get(
            f"/users/{test_user_data['username']}/profile"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "status" in data
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_user_profile_by_username_nonexistent(
        self, client_with_auth: AsyncClient
    ):
        """Test getting profile of non-existent user."""
        response = await client_with_auth.get("/users/nonexistentuser/profile")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_profile_with_bookmarks(
        self, client_with_auth: AsyncClient, test_user_data: dict
    ):
        """Test that user profile includes bookmarks."""
        # Create some bookmarks
        urls = ["https://www.google.com", "https://www.github.com"]

        for url in urls:
            await client_with_auth.post("/bookmarks/", json={"original_url": url})

        # Get user profile
        response = await client_with_auth.get(
            f"/users/{test_user_data['username']}/profile"
        )

        assert response.status_code == 200
        data = response.json()
        assert "bookmarks" in data
        assert len(data["bookmarks"]) == 2

        # Verify bookmarks structure
        for bookmark in data["bookmarks"]:
            assert "id" in bookmark
            assert "original_url" in bookmark
            assert "short_code" in bookmark
            assert "visit_count" in bookmark
