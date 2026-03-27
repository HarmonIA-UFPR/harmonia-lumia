from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.settings import settings

# O engine e o sessionmaker são criados APENAS UMA VEZ quando o app sobe
engine = create_async_engine(settings.DATABASE_URL_PG, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Esta função funciona como nosso "Manager" para o FastAPI
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
