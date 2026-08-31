import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests: defaultdict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client = request.client
        client_ip = client.host if client is not None else "127.0.0.1"
        current_time = time.time()

        # Remove requests outside the time window
        self.requests[client_ip] = [
            timestamp
            for timestamp in self.requests[client_ip]
            if current_time - timestamp < self.window
        ]

        # Check limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
            )

        # Record this request
        self.requests[client_ip].append(current_time)

        response = await call_next(request)

        return response
