"""
Pytest configuration and fixtures for testing.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }


@pytest.fixture
def sample_waste_data() -> dict:
    """Sample waste record data for testing."""
    return {
        "organization_id": "00000000-0000-0000-0000-000000000001",
        "waste_type": "plastic",
        "plastic_type": "PET",
        "source": "collection_center",
        "collection_date": "2024-01-15T10:00:00Z",
        "quantity": 1000.0,
        "unit": "kg",
        "processing_method": "recycling"
    }


@pytest.fixture
def sample_biochar_data() -> dict:
    """Sample biochar record data for testing."""
    return {
        "organization_id": "00000000-0000-0000-0000-000000000001",
        "production_date": "2024-01-15T10:00:00Z",
        "feedstock_type": "wood",
        "feedstock_quantity": 1000.0,
        "feedstock_unit": "kg",
        "biochar_quantity": 300.0,
        "biochar_unit": "kg",
        "biochar_yield_percentage": 30.0,
        "carbon_content": 70.0
    }