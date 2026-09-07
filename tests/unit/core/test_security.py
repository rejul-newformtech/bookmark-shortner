"""Test cases for security and hashing functions."""

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    get_hashed_password,
    verify_access_token,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    @pytest.mark.asyncio
    async def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!@#"
        hashed = await get_hashed_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)

    @pytest.mark.asyncio
    async def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "TestPassword123!@#"
        hashed = await get_hashed_password(password)

        assert await verify_password(password, hashed) is True

    @pytest.mark.asyncio
    async def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "TestPassword123!@#"
        wrong_password = "WrongPassword456!@#"
        hashed = await get_hashed_password(password)

        assert await verify_password(wrong_password, hashed) is False

    @pytest.mark.asyncio
    async def test_hash_consistency(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "TestPassword123!@#"
        hash1 = await get_hashed_password(password)
        hash2 = await get_hashed_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify with same password
        assert await verify_password(password, hash1) is True
        assert await verify_password(password, hash2) is True

    @pytest.mark.asyncio
    async def test_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123!@#"
        wrong_case = "testpassword123!@#"
        hashed = await get_hashed_password(password)

        assert await verify_password(wrong_case, hashed) is False

    @pytest.mark.asyncio
    async def test_empty_password_hash(self):
        """Test hashing empty password."""
        password = ""
        hashed = await get_hashed_password(password)

        assert hashed != password


class TestTokenGeneration:
    """Test JWT token creation and verification."""

    def test_create_and_verify_token(self):
        """Test creating and verifying access token."""
        token = create_access_token(data={"sub": "testuser"})
        assert isinstance(token, str)
        username = verify_access_token(token)
        assert username == "testuser"

    def test_verify_invalid_token(self):
        """Test verifying invalid token raises error."""
        with pytest.raises(JWTError):
            verify_access_token("invalid.jwt.token")
