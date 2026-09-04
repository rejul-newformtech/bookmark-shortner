from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.concurrency import shutdown_threadpool
from app.core.exceptions import exception_handlers
from app.middleware.ratelimiter import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        shutdown_threadpool()


app = FastAPI(
    title="Link Shortener API",
    version="1.0.0",
    description="This is a simple API for shortening URLs.",
    exception_handlers=exception_handlers,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=10, window=60)

app.include_router(api_router)
