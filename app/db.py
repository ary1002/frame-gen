from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import get_settings

_engine = None
_session_factory = None
_use_null_pool = False


def configure_null_pool():
    """Call once in Celery worker_process_init before any engine is created."""
    global _use_null_pool
    _use_null_pool = True


def _make_engine():
    kwargs = {"echo": False}
    if _use_null_pool:
        kwargs["poolclass"] = NullPool
    else:
        kwargs["pool_pre_ping"] = True
    return create_async_engine(get_settings().DATABASE_URL, **kwargs)


def get_engine():
    global _engine, _session_factory
    if _engine is None:
        _engine = _make_engine()
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


def reset_engine():
    """Call in Celery worker_process_init to drop the inherited connection pool."""
    global _engine, _session_factory
    _engine = None
    _session_factory = None


class AsyncSessionLocal:
    """Proxy so existing `async with AsyncSessionLocal() as db` calls keep working."""
    def __new__(cls):
        get_engine()  # ensure factory is initialised
        return _session_factory()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
