"""Test cases for bookmark endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateBookmark:
    """Test bookmark creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_bookmark_success(self, client_with_auth: AsyncClient):
        """Test successful bookmark creation."""
        bookmark_data = {"original_url": "https://www.example.com"}
        response = await client_with_auth.post("/bookmarks/", json=bookmark_data)

        assert response.status_code == 200
        data = response.json()
        assert "https://www.example.com" in str(data["original_url"])
        assert "short_code" in data
        assert "id" in data
        assert "visit_count" in data
        assert data["visit_count"] == 0

    @pytest.mark.asyncio
    async def test_create_bookmark_multiple(self, client_with_auth: AsyncClient):
        """Test creating multiple bookmarks."""
        urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
        ]

        for url in urls:
            response = await client_with_auth.post(
                "/bookmarks/", json={"original_url": url}
            )
            assert response.status_code == 200
            assert url in str(response.json()["original_url"])

    @pytest.mark.asyncio
    async def test_create_bookmark_without_auth(self, client: AsyncClient):
        """Test bookmark creation without authentication."""
        bookmark_data = {"original_url": "https://www.example.com"}
        response = await client.post("/bookmarks/", json=bookmark_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_bookmark_invalid_url(self, client_with_auth: AsyncClient):
        """Test bookmark creation with invalid URL."""
        bookmark_data = {"original_url": "not-a-valid-url"}
        response = await client_with_auth.post("/bookmarks/", json=bookmark_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_bookmark_empty_url(self, client_with_auth: AsyncClient):
        """Test bookmark creation with empty URL."""
        bookmark_data = {"original_url": ""}
        response = await client_with_auth.post("/bookmarks/", json=bookmark_data)

        assert response.status_code == 422


class TestGetBookmarks:
    """Test bookmark retrieval endpoints."""

    @pytest.mark.asyncio
    async def test_get_all_bookmarks_empty(self, client_with_auth: AsyncClient):
        """Test getting bookmarks when none exist."""
        response = await client_with_auth.get("/bookmarks/")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_all_bookmarks(self, client_with_auth: AsyncClient):
        """Test getting all bookmarks for authenticated user."""
        # Create bookmarks
        urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://www.stackoverflow.com",
        ]

        created_bookmarks = []
        for url in urls:
            response = await client_with_auth.post(
                "/bookmarks/", json={"original_url": url}
            )
            created_bookmarks.append(response.json())

        # Get all bookmarks
        response = await client_with_auth.get("/bookmarks/")
        assert response.status_code == 200
        bookmarks = response.json()
        assert len(bookmarks) == 3

        # Verify all bookmarks are returned
        for bookmark in bookmarks:
            assert "id" in bookmark
            assert "original_url" in bookmark
            assert "short_code" in bookmark

    @pytest.mark.asyncio
    async def test_get_all_bookmarks_without_auth(self, client: AsyncClient):
        """Test getting bookmarks without authentication."""
        response = await client.get("/bookmarks/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_bookmark_by_short_code_success(
        self, client_with_auth: AsyncClient
    ):
        """Test getting a specific bookmark by short code."""
        # Create a bookmark
        bookmark_data = {"original_url": "https://www.example.com"}
        create_response = await client_with_auth.post("/bookmarks/", json=bookmark_data)
        short_code = create_response.json()["short_code"]

        # Get bookmark by short code
        response = await client_with_auth.get(f"/bookmarks/{short_code}")

        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == short_code
        assert "example.com" in str(data["original_url"])

    @pytest.mark.asyncio
    async def test_get_bookmark_by_short_code_not_found(
        self, client_with_auth: AsyncClient
    ):
        """Test getting bookmark with non-existent short code."""
        response = await client_with_auth.get("/bookmarks/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_bookmark_by_short_code_without_auth(self, client: AsyncClient):
        """Test getting bookmark without authentication."""
        response = await client.get("/bookmarks/abc123")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_bookmark_background_visit_analytics(
        self, client_with_auth: AsyncClient
    ):
        """Test that accessing a bookmark triggers background visit analytics."""
        # Create a bookmark
        bookmark_data = {"original_url": "https://www.example.com"}
        create_response = await client_with_auth.post("/bookmarks/", json=bookmark_data)
        assert create_response.status_code == 200
        short_code = create_response.json()["short_code"]

        # Fetch bookmark via short code (triggers BackgroundTasks)
        response = await client_with_auth.get(f"/bookmarks/{short_code}")
        assert response.status_code == 200

        # Fetch all bookmarks to check that visit_count was updated in the background
        list_response = await client_with_auth.get("/bookmarks/")
        assert list_response.status_code == 200
        bookmarks = list_response.json()
        assert len(bookmarks) == 1
        assert bookmarks[0]["visit_count"] == 1
