from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pgvector.asyncpg import register_vector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event

from scoutr.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False, # will log every SQL statement
    pool_pre_ping=True # check if a connection is alive before using it
)

_session_factory = async_sessionmaker(engine, expire_on_commit=False)

@event.listens_for(engine.sync_engine, "connect")
def _register_vector(dbapi_conn, _record) -> None:
    # asyncpg exposes the raw connection here; register the vector codec on it.
    dbapi_conn.run_async(register_vector)

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a session; commit on success, roll back on error, always close."""
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise