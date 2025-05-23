from abc import abstractmethod
from asyncio import current_task
from typing import override

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from archipy.adapters.base.sqlalchemy.session_manager_ports import AsyncSessionManagerPort, SessionManagerPort
from archipy.configs.config_template import SQLAlchemyConfig
from archipy.models.errors.custom_errors import InvalidArgumentError


class BaseSQLAlchemySessionManager(SessionManagerPort):
    """Base synchronous SQLAlchemy session manager.

    Implements the SessionManagerPort interface to provide session management for
    synchronous database operations. Database-specific session managers should inherit
    from this class and implement database-specific engine creation.

    Args:
        orm_config: SQLAlchemy configuration. Must match the expected config type for the database.
    """

    def __init__(self, orm_config: SQLAlchemyConfig) -> None:
        """Initialize the base session manager.

        Args:
            orm_config: SQLAlchemy configuration.

        Raises:
            InvalidArgumentError: If the configuration type is invalid.
        """
        if not isinstance(orm_config, self._expected_config_type()):
            raise InvalidArgumentError(
                f"Expected {self._expected_config_type().__name__}, got {type(orm_config).__name__}",
            )
        self.engine = self._create_engine(orm_config)
        self._session_generator = self._get_session_generator()

    @abstractmethod
    def _expected_config_type(self) -> type[SQLAlchemyConfig]:
        """Return the expected configuration type for the database.

        Returns:
            The SQLAlchemy configuration class expected by this session manager.
        """
        pass

    def _create_engine(self, configs: SQLAlchemyConfig) -> Engine:
        """Create a SQLAlchemy engine with common configuration.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            A configured SQLAlchemy engine.
        """
        url = self._create_url(configs)
        return create_engine(
            url,
            isolation_level=configs.ISOLATION_LEVEL,
            echo=configs.ECHO,
            echo_pool=configs.ECHO_POOL,
            enable_from_linting=configs.ENABLE_FROM_LINTING,
            hide_parameters=configs.HIDE_PARAMETERS,
            pool_pre_ping=configs.POOL_PRE_PING,
            pool_size=configs.POOL_SIZE,
            pool_recycle=configs.POOL_RECYCLE_SECONDS,
            pool_reset_on_return=configs.POOL_RESET_ON_RETURN,
            pool_timeout=configs.POOL_TIMEOUT,
            pool_use_lifo=configs.POOL_USE_LIFO,
            query_cache_size=configs.QUERY_CACHE_SIZE,
            max_overflow=configs.POOL_MAX_OVERFLOW,
            connect_args=self._get_connect_args(),
        )

    @abstractmethod
    def _create_url(self, configs: SQLAlchemyConfig) -> URL:
        """Create a database connection URL.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            A SQLAlchemy URL object for the database.
        """
        pass

    def _get_connect_args(self) -> dict:
        """Return additional connection arguments for the engine.

        Returns:
            A dictionary of connection arguments (default is empty).
        """
        return {}

    def _get_session_generator(self) -> scoped_session:
        """Create a scoped session factory for synchronous sessions.

        Returns:
            A scoped_session instance used by `get_session` to provide thread-safe sessions.
        """
        session_maker = sessionmaker(self.engine)
        return scoped_session(session_maker)

    @override
    def get_session(self) -> Session:
        """Retrieve a thread-safe SQLAlchemy session.

        Returns:
            Session: A SQLAlchemy session instance for database operations.
        """
        return self._session_generator()  # type: ignore[no-any-return]

    @override
    def remove_session(self) -> None:
        """Remove the current session from the registry.

        Cleans up the session to prevent resource leaks, typically called at the end
        of a request.
        """
        self._session_generator.remove()


class AsyncBaseSQLAlchemySessionManager(AsyncSessionManagerPort):
    """Base asynchronous SQLAlchemy session manager.

    Implements the AsyncSessionManagerPort interface to provide session management for
    asynchronous database operations. Database-specific session managers should inherit
    from this class and implement database-specific async engine creation.

    Args:
        orm_config: SQLAlchemy configuration. Must match the expected config type for the database.
    """

    def __init__(self, orm_config: SQLAlchemyConfig) -> None:
        """Initialize the base async session manager.

        Args:
            orm_config: SQLAlchemy configuration.

        Raises:
            InvalidArgumentError: If the configuration type is invalid.
        """
        if not isinstance(orm_config, self._expected_config_type()):
            raise InvalidArgumentError(
                f"Expected {self._expected_config_type().__name__}, got {type(orm_config).__name__}",
            )
        self.engine = self._create_async_engine(orm_config)
        self._session_generator = self._get_session_generator()

    @abstractmethod
    def _expected_config_type(self) -> type[SQLAlchemyConfig]:
        """Return the expected configuration type for the database.

        Returns:
            The SQLAlchemy configuration class expected by this session manager.
        """
        pass

    def _create_async_engine(self, configs: SQLAlchemyConfig) -> AsyncEngine:
        """Create an async SQLAlchemy engine with common configuration.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            A configured async SQLAlchemy engine.
        """
        url = self._create_url(configs)
        return create_async_engine(
            url,
            isolation_level=configs.ISOLATION_LEVEL,
            echo=configs.ECHO,
            echo_pool=configs.ECHO_POOL,
            enable_from_linting=configs.ENABLE_FROM_LINTING,
            hide_parameters=configs.HIDE_PARAMETERS,
            pool_pre_ping=configs.POOL_PRE_PING,
            pool_size=configs.POOL_SIZE,
            pool_recycle=configs.POOL_RECYCLE_SECONDS,
            pool_reset_on_return=configs.POOL_RESET_ON_RETURN,
            pool_timeout=configs.POOL_TIMEOUT,
            pool_use_lifo=configs.POOL_USE_LIFO,
            query_cache_size=configs.QUERY_CACHE_SIZE,
            max_overflow=configs.POOL_MAX_OVERFLOW,
            connect_args=self._get_connect_args(),
        )

    @abstractmethod
    def _create_url(self, configs: SQLAlchemyConfig) -> URL:
        """Create a database connection URL for async connections.

        Args:
            configs: SQLAlchemy configuration.

        Returns:
            A SQLAlchemy URL object for the database.
        """
        pass

    def _get_connect_args(self) -> dict:
        """Return additional connection arguments for the async engine.

        Returns:
            A dictionary of connection arguments (default is empty).
        """
        return {}

    def _get_session_generator(self) -> async_scoped_session:
        """Create a scoped session factory for async sessions.

        Returns:
            An async_scoped_session instance used by `get_session` to provide task-safe async sessions.
        """
        session_maker = async_sessionmaker(self.engine)
        return async_scoped_session(session_maker, scopefunc=current_task)

    @override
    def get_session(self) -> AsyncSession:
        """Retrieve a task-safe async SQLAlchemy session.

        Returns:
            AsyncSession: An async SQLAlchemy session instance for database operations.
        """
        return self._session_generator()  # type: ignore[no-any-return]

    @override
    async def remove_session(self) -> None:
        """Asynchronously remove the current session from the registry.

        Cleans up the async session to prevent resource leaks, typically called at
        the end of an async request.
        """
        await self._session_generator.remove()
