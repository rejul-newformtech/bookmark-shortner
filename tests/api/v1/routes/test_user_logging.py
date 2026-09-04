"""Tests for user ID logging once per request."""

import logging

import pytest
from httpx import AsyncClient


class TestUserLogging:
    """Test user ID logging behavior."""

    @pytest.mark.asyncio
    async def test_authenticated_request_logs_user_id_once(
        self, client_with_auth: AsyncClient, caplog: pytest.LogCaptureFixture
    ):
        """Test that an authenticated request logs the user ID exactly once."""
        with caplog.at_level(logging.INFO):
            response = await client_with_auth.get("/users/profile")

        assert response.status_code == 200
        user_id = response.json()["id"]

        matching_logs = [
            record
            for record in caplog.records
            if f"Request initiated for user_id={user_id}" in record.message
        ]
        # Must be logged exactly once for this request
        assert len(matching_logs) == 1

    @pytest.mark.asyncio
    async def test_subsequent_request_logs_once_for_itself(
        self, client_with_auth: AsyncClient, caplog: pytest.LogCaptureFixture
    ):
        """Test that separate requests each log once."""
        with caplog.at_level(logging.INFO):
            caplog.clear()
            resp1 = await client_with_auth.get("/users/profile")
            assert resp1.status_code == 200
            user_id = resp1.json()["id"]

            records_req1 = [
                r
                for r in caplog.records
                if f"Request initiated for user_id={user_id}" in r.message
            ]
            assert len(records_req1) == 1

            caplog.clear()
            resp2 = await client_with_auth.get("/bookmarks/")
            assert resp2.status_code == 200

            records_req2 = [
                r
                for r in caplog.records
                if f"Request initiated for user_id={user_id}" in r.message
            ]
            assert len(records_req2) == 1

    @pytest.mark.asyncio
    async def test_unauthenticated_request_does_not_log_user_id(
        self, client: AsyncClient, caplog: pytest.LogCaptureFixture
    ):
        """Test that unauthenticated requests do not log a user ID."""
        with caplog.at_level(logging.INFO):
            response = await client.get("/users/profile")

        assert response.status_code == 401
        matching_logs = [
            record
            for record in caplog.records
            if "Request initiated for user_id=" in record.message
        ]
        assert len(matching_logs) == 0
