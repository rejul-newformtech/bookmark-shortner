import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.middleware.ratelimiter import RateLimitMiddleware

# Use in-memory SQLite for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.new_event_loop()
        yield loop
    finally:
        loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession]:
    """Get test database session."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test to avoid cross-test 429s."""
    stack = getattr(app, "middleware_stack", None)
    while stack is not None:
        if isinstance(stack, RateLimitMiddleware):
            stack.requests.clear()
            break
        stack = getattr(stack, "app", None)


@pytest.fixture(autouse=True)
def override_get_db(db_session, monkeypatch, db_engine):
    """Override the get_db dependency and patch AsyncSessionLocal for background tasks."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    test_sessionmaker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    monkeypatch.setattr("app.db.session.AsyncSessionLocal", test_sessionmaker)
    monkeypatch.setattr("app.service.analytics.AsyncSessionLocal", test_sessionmaker)


@pytest_asyncio.fixture
async def client(override_get_db):
    """Get test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user_data():
    """Provide test user data."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "ValidPass123!@#",
    }


@pytest.fixture
async def test_user_data_2():
    """Provide another test user data."""
    return {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password": "ValidPass456!@#",
    }


@pytest.fixture
async def registered_user(client, test_user_data):
    """Register and return a test user."""
    response = await client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
async def auth_token(client, test_user_data):
    """Get authentication token for test user."""
    # Register user
    await client.post("/auth/register", json=test_user_data)

    # Login and get token
    response = await client.post(
        "/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def client_with_auth(override_get_db, auth_token):
    """Get a separate test client with authorization header set."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as ac:
        yield ac


@pytest.fixture
def sample_urls() -> list[str]:
    """Provide a list of sample URLs for testing."""
    return [
        "https://python.org",
        "https://fastapi.tiangolo.com",
        "https://github.com",
    ]
