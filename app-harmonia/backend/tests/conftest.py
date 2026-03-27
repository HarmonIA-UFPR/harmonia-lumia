import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.infrastructure.database.models.base import table_registry
from app.infrastructure.database.models.tool_model import ToolModel  # noqa
from app.infrastructure.database.models.user_model import UserModel  # noqa
from app.infrastructure.database.session import get_session
from app.main import app

# Use SQLite in-memory para testes assíncronos
SQLALCHEMY_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest_asyncio.fixture(scope='function')
async def db_session():
    """Setup de banco de dados por teste."""
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)
        await conn.run_sync(table_registry.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def client(db_session):
    """
    Client assíncrono do FastAPI para testes,
    injetando a sessão do teste.
    """

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
