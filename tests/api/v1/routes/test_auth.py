"""Test cases for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestUserRegistration:
    """Test user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test successful user registration."""
        response = await client.post("/auth/register", json=test_user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["user"]["username"] == test_user_data["username"]
        assert data["user"]["email"] == test_user_data["email"]
        assert "id" in data["user"]
        assert "hashed_password" not in data["user"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with duplicate username."""
        # Register first user
        await client.post("/auth/register", json=test_user_data)

        # Try to register with same username
        duplicate_data = {**test_user_data, "email": "different@example.com"}
        response = await client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with duplicate email."""
        # Register first user
        await client.post("/auth/register", json=test_user_data)

        # Try to register with same email
        duplicate_data = {**test_user_data, "username": "differentuser"}
        response = await client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        invalid_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "ValidPass123!@#",
        }
        response = await client.post("/auth/register", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_username(self, client: AsyncClient):
        """Test registration with username too short."""
        short_username_data = {
            "username": "ab",  # Min length is 3
            "email": "test@example.com",
            "password": "ValidPass123!@#",
        }
        response = await client.post("/auth/register", json=short_username_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with password too short."""
        short_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Sh1!@",  # 5 chars, below min_length=8
        }
        response = await client.post("/auth/register", json=short_password_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_password_no_lowercase(self, client: AsyncClient):
        """Test registration with password missing lowercase letter."""
        invalid_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NOLOWECASE123!@#",
        }
        response = await client.post("/auth/register", json=invalid_password_data)

        assert response.status_code == 422
        assert "lowercase letter" in response.json()["detail"][0]["msg"]

    @pytest.mark.asyncio
    async def test_register_password_no_uppercase(self, client: AsyncClient):
        """Test registration with password missing uppercase letter."""
        invalid_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "nouppercase123!@#",
        }
        response = await client.post("/auth/register", json=invalid_password_data)

        assert response.status_code == 422
        assert "uppercase letter" in response.json()["detail"][0]["msg"]

    @pytest.mark.asyncio
    async def test_register_password_no_digit(self, client: AsyncClient):
        """Test registration with password missing digit."""
        invalid_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoDigitHere!@#$",
        }
        response = await client.post("/auth/register", json=invalid_password_data)

        assert response.status_code == 422
        assert "digit" in response.json()["detail"][0]["msg"]

    @pytest.mark.asyncio
    async def test_register_password_no_special_char(self, client: AsyncClient):
        """Test registration with password missing special character."""
        invalid_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoSpecialChar123",
        }
        response = await client.post("/auth/register", json=invalid_password_data)

        assert response.status_code == 422
        assert "special character" in response.json()["detail"][0]["msg"]


class TestUserLogin:
    """Test user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful login."""
        # Register user
        await client.post("/auth/register", json=test_user_data)

        # Login
        response = await client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_username(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test login with non-existent username."""
        # Register user
        await client.post("/auth/register", json=test_user_data)

        # Try to login with wrong username
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistentuser",
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test login with incorrect password."""
        # Register user
        await client.post("/auth/register", json=test_user_data)

        # Try to login with wrong password
        response = await client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"],
                "password": "WrongPassword123!@#",
            },
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_case_sensitive_username(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test that login is case-sensitive for username."""
        # Register user
        await client.post("/auth/register", json=test_user_data)

        # Try to login with different case
        response = await client.post(
            "/auth/login",
            data={
                "username": test_user_data["username"].upper(),
                "password": test_user_data["password"],
            },
        )

        # Should fail if username is case-sensitive
        assert response.status_code in [400, 401]
