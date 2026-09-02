"""Integration tests for complete workflows."""

import pytest
from httpx import AsyncClient


class TestCompleteUserWorkflow:
    """Test complete user registration and authentication workflow."""

    @pytest.mark.asyncio
    async def test_register_and_login_workflow(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test complete registration and login workflow."""
        # Step 1: Register user
        register_response = await client.post("/auth/register", json=test_user_data)
        assert register_response.status_code == 200

        # Step 2: Login with registered credentials
        login_response = await client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert token is not None

        # Step 3: Use token to access protected endpoint
        client.headers = {"Authorization": f"Bearer {token}"}
        profile_response = await client.get("/users/profile")
        assert profile_response.status_code == 200
        assert profile_response.json()["username"] == test_user_data["username"]


class TestCompleteBookmarkWorkflow:
    """Test complete bookmark management workflow."""

    @pytest.mark.asyncio
    async def test_create_read_bookmark_workflow(self, client_with_auth: AsyncClient):
        """Test complete bookmark create and read lifecycle."""
        # Step 1: Create bookmark
        bookmark_url = "https://www.example.com"
        create_response = await client_with_auth.post(
            "/bookmarks/", json={"original_url": bookmark_url}
        )
        assert create_response.status_code == 200
        bookmark = create_response.json()
        bookmark_id = bookmark["id"]
        short_code = bookmark["short_code"]

        # Step 2: Retrieve all bookmarks
        list_response = await client_with_auth.get("/bookmarks/")
        assert list_response.status_code == 200
        bookmarks = list_response.json()
        assert len(bookmarks) == 1

        # Step 3: Retrieve specific bookmark by short code
        get_response = await client_with_auth.get(f"/bookmarks/{short_code}")
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["id"] == bookmark_id
        assert "example.com" in str(retrieved["original_url"])


class TestMultipleUsersWorkflow:
    """Test workflows with multiple users."""

    @pytest.mark.asyncio
    async def test_user_isolation(
        self, client: AsyncClient, test_user_data: dict, test_user_data_2: dict
    ):
        """Test that users are isolated and can't access each other's data."""
        # User 1: Register and create bookmark
        await client.post("/auth/register", json=test_user_data)
        login1 = await client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )
        token1 = login1.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token1}"}

        create1 = await client.post(
            "/bookmarks/", json={"original_url": "https://user1.com"}
        )
        assert create1.status_code == 200

        # User 1: Get bookmarks (should have 1)
        list1 = await client.get("/bookmarks/")
        assert len(list1.json()) == 1

        # User 2: Register and create bookmark
        client.headers = {}  # Clear auth
        await client.post("/auth/register", json=test_user_data_2)
        login2 = await client.post(
            "/auth/login",
            data={
                "username": test_user_data_2["username"],
                "password": test_user_data_2["password"],
            },
        )
        token2 = login2.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token2}"}

        create2 = await client.post(
            "/bookmarks/", json={"original_url": "https://user2.com"}
        )
        assert create2.status_code == 200

        # User 2: Get bookmarks (should have 1, not 2)
        list2 = await client.get("/bookmarks/")
        assert len(list2.json()) == 1

        # User 2: Get profile and verify isolation
        profile_response = await client.get("/users/profile")
        assert profile_response.status_code == 200
        assert profile_response.json()["username"] == test_user_data_2["username"]


class TestErrorHandlingWorkflow:
    """Test error handling in various workflows."""

    @pytest.mark.asyncio
    async def test_unauthorized_access_denied(
        self, client: AsyncClient, client_with_auth: AsyncClient
    ):
        """Test that unauthorized users cannot access protected endpoints."""
        # Create bookmark as authenticated user
        create_response = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://www.example.com"}
        )
        assert create_response.status_code == 200

        # Try to access as unauthenticated user
        unauthenticated_list = await client.get("/bookmarks/")
        assert unauthenticated_list.status_code == 401

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, client: AsyncClient):
        """Test that validation errors are properly handled."""
        # Register with invalid password
        invalid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",  # Invalid: too short
        }
        response = await client.post("/auth/register", json=invalid_data)
        assert response.status_code == 422
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_duplicate_registration_error(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test that duplicate registration is properly rejected."""
        # Register user first time
        await client.post("/auth/register", json=test_user_data)

        # Try to register again with same username
        duplicate_response = await client.post(
            "/auth/register",
            json={
                "username": test_user_data["username"],
                "email": "different@example.com",
                "password": test_user_data["password"],
            },
        )
        assert duplicate_response.status_code == 400
        assert "already exists" in duplicate_response.json()["detail"]


class TestDataConsistency:
    """Test data consistency across operations."""

    @pytest.mark.asyncio
    async def test_user_profile_consistency(
        self, client_with_auth: AsyncClient, test_user_data: dict
    ):
        """Test that user profile data is consistent."""
        # Create a bookmark
        await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://www.example.com"}
        )

        # Get user profile
        profile_response = await client_with_auth.get("/users/profile")

        assert profile_response.status_code == 200
        data = profile_response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert "status" in data
        assert "created_at" in data
        assert "bookmarks" in data
        assert len(data["bookmarks"]) == 1
