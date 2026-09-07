"""Test cases for user schemas."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse


class TestUserCreateSchema:
    """Test UserCreate schema validation."""

    def test_valid_user_create(self):
        """Test creating valid user."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "ValidPass123!@#",
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "ValidPass123!@#"

    def test_username_min_length(self):
        """Test username minimum length validation."""
        user_data = {
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "ValidPass123!@#",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "at least 3 characters" in str(exc_info.value)

    def test_username_max_length(self):
        """Test username maximum length validation."""
        user_data = {
            "username": "a" * 51,  # Too long
            "email": "test@example.com",
            "password": "ValidPass123!@#",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "at most 50 characters" in str(exc_info.value)

    def test_invalid_email_format(self):
        """Test invalid email format."""
        user_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "ValidPass123!@#",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "valid email address" in str(exc_info.value)

    def test_password_requires_lowercase(self):
        """Test password lowercase requirement."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NOLOWECASE123!@#",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "lowercase letter" in str(exc_info.value)

    def test_password_requires_uppercase(self):
        """Test password uppercase requirement."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "nouppercase123!@#",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "uppercase letter" in str(exc_info.value)

    def test_password_requires_digit(self):
        """Test password digit requirement."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoDigitHere!@#$",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "digit" in str(exc_info.value)

    def test_password_requires_special_char(self):
        """Test password special character requirement."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "NoSpecialChar123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        assert "special character" in str(exc_info.value)


class TestUserResponseSchema:
    """Test UserResponse schema."""

    def test_user_response_from_dict(self):
        """Test creating UserResponse from dictionary."""
        user_dict = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "status": "active",
        }
        user = UserResponse(**user_dict)
        assert user.username == "testuser"
        assert user.status == "active"

    def test_user_response_excludes_password(self):
        """Test that UserResponse doesn't include password."""
        user_dict = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "status": "active",
        }
        user = UserResponse(**user_dict)
        assert not hasattr(user, "password")
        assert not hasattr(user, "hashed_password")
