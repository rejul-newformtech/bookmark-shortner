"""Test cases for user CRUD operations."""

import pytest
from fastapi import HTTPException

from app.crud.user import user_service
from app.models.users import UserStatus
from app.schemas.user import UserCreate


class TestUserCRUD:
    """Test user CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!@#",
        )

        user = await user_service.create_user(db_session, user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.status == UserStatus.ACTIVE
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_get_user_by_username(self, db_session):
        """Test getting user by username."""
        # Create user
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!@#",
        )
        created_user = await user_service.create_user(db_session, user_data)

        # Get user
        retrieved_user = await user_service.get_user_profile_by_username(
            db_session, "testuser"
        )

        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, db_session):
        """Test getting non-existent user raises error."""
        with pytest.raises(HTTPException):
            await user_service.get_user_profile_by_username(db_session, "nonexistent")

    @pytest.mark.asyncio
    async def test_duplicate_username_error(self, db_session):
        """Test that duplicate username raises error."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!@#",
        )
        await user_service.create_user(db_session, user_data)

        duplicate_data = UserCreate(
            username="testuser",
            email="different@example.com",
            password="ValidPass123!@#",
        )

        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(db_session, duplicate_data)
        assert "Username already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_duplicate_email_error(self, db_session):
        """Test that duplicate email raises error."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123!@#",
        )
        await user_service.create_user(db_session, user_data)

        duplicate_data = UserCreate(
            username="differentuser",
            email="test@example.com",
            password="ValidPass123!@#",
        )

        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(db_session, duplicate_data)
        assert "Email already exists" in str(exc_info.value.detail)
