"""
Pytest configuration and fixtures.
"""

import sys
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from uuid import uuid4

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.core.database import Base, get_db
from backend.core.config import settings
from backend.main import app


# Test database URL - use a separate test database
TEST_DATABASE_URL = settings.database_url.replace("/youtuber", "/youtuber_test")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(autouse=True)
def reset_session_manager():
    """Reset session manager before each test."""
    from backend.core.session import session_manager
    session_manager._sessions.clear()
    yield
    session_manager._sessions.clear()


# ===== Database Fixtures =====

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with test database."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async def override_get_db():
        async with async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# ===== Auth Fixtures =====

@pytest.fixture
def test_user_data():
    """Return test user data."""
    return {
        "email": f"test_{uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }


@pytest_asyncio.fixture
async def authenticated_user(client: AsyncClient, test_user_data: dict):
    """Create and authenticate a test user, return user data and tokens."""
    # Signup
    response = await client.post("/auth/signup", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    
    return {
        "user": data["user"],
        "tokens": data["tokens"],
        "credentials": test_user_data,
    }


@pytest.fixture
def auth_headers(authenticated_user):
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {authenticated_user['tokens']['access_token']}"}


