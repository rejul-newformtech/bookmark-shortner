"""Test cases for RateLimitMiddleware."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from app.middleware.ratelimiter import RateLimitMiddleware


class TestRateLimitMiddleware:
    """Test rate limiter middleware logic."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_under_limit(self):
        """Test that requests within the limit pass through."""
        app = FastAPI()
        middleware = RateLimitMiddleware(app=app, max_requests=5, window=60)

        async def call_next(request):
            return JSONResponse(status_code=200, content={"status": "ok"})

        mock_request = AsyncMock(spec=Request)
        mock_request.client.host = "192.168.1.100"

        for _ in range(5):
            response = await middleware.dispatch(mock_request, call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_limit(self):
        """Test that requests exceeding the limit return 429."""
        app = FastAPI()
        middleware = RateLimitMiddleware(app=app, max_requests=3, window=60)

        async def call_next(request):
            return JSONResponse(status_code=200, content={"status": "ok"})

        mock_request = AsyncMock(spec=Request)
        mock_request.client.host = "192.168.1.200"

        for _ in range(3):
            response = await middleware.dispatch(mock_request, call_next)
            assert response.status_code == 200

        # 4th request exceeds max_requests=3
        blocked_response = await middleware.dispatch(mock_request, call_next)
        assert blocked_response.status_code == 429
