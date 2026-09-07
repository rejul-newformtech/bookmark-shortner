"""Middleware for request-scoped user logging context."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import reset_user_context


class LoggingContextMiddleware(BaseHTTPMiddleware):
    """Middleware to initialize and reset user logging context for each request."""

    async def dispatch(self, request: Request, call_next):
        reset_user_context()
        try:
            response = await call_next(request)
        finally:
            reset_user_context()
        return response
