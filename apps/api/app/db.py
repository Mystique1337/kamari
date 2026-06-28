"""Async SQLAlchemy engine/session over the self-hosted Postgres.

Created lazily — only when DATABASE_URL is set — so the gateway still runs standalone
(mock mode) with no database.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    pass


def _async_url(url: str) -> str:
    for prefix in ("postgresql+asyncpg://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            return url.replace(prefix, "postgresql+asyncpg://", 1)
    return url


_settings = get_settings()
engine = create_async_engine(_async_url(_settings.database_url)) if _settings.database_url else None
async_session_maker = async_sessionmaker(engine, expire_on_commit=False) if engine else None


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
