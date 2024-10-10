import contextlib
from typing import Any, AsyncIterator

from app.settings import settings
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    __mapper_args__ = {"eager_defaults": True}


class DatabaseSessionUninitializedException(Exception):
    def __init__(self, message="Database session is uninitialized."):
        super().__init__(message)


# Heavily inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
class DatabaseSessionManager:
    def __init__(
        self,
        host: str,
        engine_kwargs: dict[str, Any] | None = None,
    ):
        default_kwargs = {"pool_size": 100, "max_overflow": 10}
        engine_kwargs = {**default_kwargs, **(engine_kwargs or {})}
        self._engine = create_async_engine(host, **engine_kwargs)
        self._session_maker = async_sessionmaker(
            autocommit=False,
            autoflush=True,
            bind=self._engine,
            expire_on_commit=False,
        )

    async def close(self):
        if self._engine is None:
            raise DatabaseSessionUninitializedException()
        await self._engine.dispose()

        self._engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseSessionUninitializedException()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise DatabaseSessionUninitializedException()

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


session_manager = DatabaseSessionManager(settings.SQLALCHEMY_DATABASE_URI)


async def get_db():
    async with session_manager.session() as session:
        yield session
