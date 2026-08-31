from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


def _serialize_error(obj):
    """Recursively convert non-JSON-serializable objects to strings."""
    if isinstance(obj, dict):
        return {k: _serialize_error(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_error(item) for item in obj]
    elif isinstance(obj, Exception):
        return str(obj)
    else:
        return obj


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    serialized_errors = _serialize_error(errors)
    return JSONResponse(
        status_code=422,
        content={"detail": serialized_errors},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


exception_handlers: dict[Any, Any] = {
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    Exception: unhandled_exception_handler,
}
