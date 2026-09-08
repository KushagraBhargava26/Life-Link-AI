# backend/tests/conftest.py
import pytest
from app.database import close_db, get_session_factory


@pytest.fixture
async def db_session():
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


@pytest.fixture(autouse=True)
async def reset_db_engine():
    yield
    await close_db()

