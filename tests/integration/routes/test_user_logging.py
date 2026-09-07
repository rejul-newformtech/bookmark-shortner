"""Tests for user ID logging once per request."""

import logging

import pytest
from httpx import AsyncClient

from app.core.logger import (
    get_logger,
    reset_user_context,
    set_current_user_id,
)


class TestUserLogging:
    """Test user ID logging behavior."""

    def test_logger_shows_user_id_only_once_in_context(self):
        """Test that get_logger only attaches user_id to the very first log record."""
        reset_user_context()
        logger = get_logger("test_user_logger")

        test_uid = "123e4567-e89b-12d3-a456-426614174000"
        set_current_user_id(test_uid)

        # First log in this context
        record1 = logger.makeRecord(
            "test_user_logger", logging.INFO, "test.py", 10, "First message", (), None
        )
        logger.filter(record1)
        assert getattr(record1, "user_id", None) == test_uid

        # Second log in the same context
        record2 = logger.makeRecord(
            "test_user_logger", logging.INFO, "test.py", 11, "Second message", (), None
        )
        logger.filter(record2)
        assert getattr(record2, "user_id", None) is None

        # Reset context (simulates next request)
        reset_user_context()
        set_current_user_id(test_uid)
        record3 = logger.makeRecord(
            "test_user_logger", logging.INFO, "test.py", 12, "Third message", (), None
        )
        logger.filter(record3)
        assert getattr(record3, "user_id", None) == test_uid

        reset_user_context()

    @pytest.mark.asyncio
    async def test_authenticated_request_attaches_user_id(
        self, client_with_auth: AsyncClient, caplog: pytest.LogCaptureFixture
    ):
        """Test that an authenticated request attaches user_id in the logs."""
        with caplog.at_level(logging.INFO):
            response = await client_with_auth.get("/users/profile")

        assert response.status_code == 200
        user_id = response.json()["id"]

        matching_records = [
            record
            for record in caplog.records
            if getattr(record, "user_id", None) == user_id
        ]
        assert len(matching_records) == 1

    @pytest.mark.asyncio
    async def test_unauthenticated_request_does_not_attach_user_id(
        self, client: AsyncClient, caplog: pytest.LogCaptureFixture
    ):
        """Test that unauthenticated requests do not attach a user ID."""
        with caplog.at_level(logging.INFO):
            response = await client.get("/users/profile")

        assert response.status_code == 401
        matching_records = [
            record
            for record in caplog.records
            if getattr(record, "user_id", None) is not None
        ]
        assert len(matching_records) == 0
