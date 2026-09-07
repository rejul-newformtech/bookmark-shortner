"""Integration tests for /visited routes, including bookmark site fetch using bookmark_id."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestVisitsRoutes:
    """Test /visited endpoints."""

    @pytest.mark.asyncio
    async def test_fetch_bookmark_site_no_visits_yet(
        self, client_with_auth: AsyncClient
    ):
        """Fetch bookmark site info using bookmark_id when no visits have been recorded."""
        # 1. Create bookmark
        bm_res = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://fastapi.tiangolo.com"}
        )
        assert bm_res.status_code == 200
        bm_data = bm_res.json()
        bookmark_id = bm_data["id"]

        # 2. Fetch site info via /visited/bookmark/{bookmark_id}
        res = await client_with_auth.get(f"/visited/bookmark/{bookmark_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["bookmark"]["id"] == bookmark_id
        assert "fastapi.tiangolo.com" in data["bookmark"]["original_url"]
        assert data["bookmark"]["short_code"] == bm_data["short_code"]
        assert data["bookmark"]["visit_count"] == 0
        assert data["visits"] == []

    @pytest.mark.asyncio
    async def test_fetch_bookmark_site_with_visits(self, client_with_auth: AsyncClient):
        """Fetch bookmark site info and verify recorded visits are included."""
        # 1. Create bookmark
        bm_res = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://docs.python.org"}
        )
        assert bm_res.status_code == 200
        bm_data = bm_res.json()
        bookmark_id = bm_data["id"]

        # 2. Log a visit
        visit_res = await client_with_auth.post(
            "/visited/", json={"bookmark_id": bookmark_id}
        )
        assert visit_res.status_code == 200
        visit_id = visit_res.json()["id"]

        # 3. Fetch site info via /visited/bookmark/{bookmark_id}
        res = await client_with_auth.get(f"/visited/bookmark/{bookmark_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["bookmark"]["id"] == bookmark_id
        assert "docs.python.org" in data["bookmark"]["original_url"]
        assert len(data["visits"]) >= 1
        assert any(v["id"] == visit_id for v in data["visits"])
        # Verify visit also has the bookmark populated
        assert data["visits"][0]["bookmark"]["id"] == bookmark_id

    @pytest.mark.asyncio
    async def test_fetch_bookmark_site_not_found(self, client_with_auth: AsyncClient):
        """Non-existent bookmark_id returns 404."""
        random_id = str(uuid4())
        res = await client_with_auth.get(f"/visited/bookmark/{random_id}")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fetch_bookmark_site_unauthorized(self, client: AsyncClient):
        """Unauthenticated request returns 401."""
        random_id = str(uuid4())
        res = await client.get(f"/visited/bookmark/{random_id}")
        assert res.status_code == 401

    @pytest.mark.asyncio
    async def test_fetch_bookmark_site_other_user_isolation(
        self,
        client: AsyncClient,
        client_with_auth: AsyncClient,
        test_user_data_2: dict,
    ):
        """User cannot fetch bookmark site info for a bookmark owned by another user."""
        # User 1 creates bookmark
        bm_res = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://secret-site.org"}
        )
        assert bm_res.status_code == 200
        bookmark_id = bm_res.json()["id"]

        # Register and login User 2
        await client.post("/auth/register", json=test_user_data_2)
        login_res = await client.post(
            "/auth/login",
            data={
                "username": test_user_data_2["username"],
                "password": test_user_data_2["password"],
            },
        )
        token2 = login_res.json()["access_token"]
        client.headers = {"Authorization": f"Bearer {token2}"}

        # User 2 tries to fetch User 1's bookmark site
        res = await client.get(f"/visited/bookmark/{bookmark_id}")
        assert res.status_code == 404

    @pytest.mark.asyncio
    async def test_filter_visits_by_bookmark_id(self, client_with_auth: AsyncClient):
        """Test GET /visited/?bookmark_id={bookmark_id} query parameter."""
        bm_res = await client_with_auth.post(
            "/bookmarks/", json={"original_url": "https://filter-test.org"}
        )
        assert bm_res.status_code == 200
        bookmark_id = bm_res.json()["id"]

        # Log a visit
        await client_with_auth.post("/visited/", json={"bookmark_id": bookmark_id})

        # Query with bookmark_id
        res = await client_with_auth.get(f"/visited/?bookmark_id={bookmark_id}")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1
        assert all(v["bookmark_id"] == bookmark_id for v in data)
