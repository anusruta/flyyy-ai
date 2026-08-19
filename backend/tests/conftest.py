import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

from app.models.models import Base as AppBase
from app.database import get_db
from app.main import app

_test_engine = None
_TestSession = None


async def _get_test_engine():
    global _test_engine, _TestSession
    if _test_engine is None:
        _test_engine = create_async_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        _TestSession = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)
        async with _test_engine.begin() as conn:
            await conn.run_sync(AppBase.metadata.create_all)
    return _test_engine, _TestSession


async def override_get_db():
    _, TestSession = await _get_test_engine()
    async with TestSession() as session:
        yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    await _get_test_engine()
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
