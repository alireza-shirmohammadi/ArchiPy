from typing import override

from archipy.adapters.base.sqlalchemy.adapters import AsyncBaseSQLAlchemyAdapter, BaseSQLAlchemyAdapter
from archipy.adapters.sqlite.sqlalchemy.session_managers import (
    AsyncSqliteSQlAlchemySessionManager,
    SqliteSQlAlchemySessionManager,
)
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import SqliteSQLAlchemyConfig


class SqliteSQLAlchemyAdapter(BaseSQLAlchemyAdapter):
    """Synchronous SQLAlchemy adapter for SQLite.

    Inherits from BaseSQLAlchemyAdapter to provide SQLite-specific session management
    and database operations, typically used for in-memory testing.

    Args:
        orm_config: SQLite-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: SqliteSQLAlchemyConfig | None = None) -> None:
        """Initialize the SQLite adapter with a session manager.

        Args:
            orm_config: SQLite-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLITE_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _create_session_manager(self, configs: SqliteSQLAlchemyConfig) -> SqliteSQlAlchemySessionManager:
        """Create a SQLite-specific session manager.

        Args:
            configs: SQLite configuration.

        Returns:
            A SQLite session manager instance.
        """
        return SqliteSQlAlchemySessionManager(configs)


class AsyncSqliteSQLAlchemyAdapter(AsyncBaseSQLAlchemyAdapter):
    """Asynchronous SQLAlchemy adapter for SQLite.

    Inherits from AsyncBaseSQLAlchemyAdapter to provide async SQLite-specific session
    management and database operations, typically used for in-memory testing.

    Args:
        orm_config: SQLite-specific configuration. If None, uses global config.
    """

    def __init__(self, orm_config: SqliteSQLAlchemyConfig | None = None) -> None:
        """Initialize the async SQLite adapter with a session manager.

        Args:
            orm_config: SQLite-specific configuration. If None, uses global config.
        """
        configs = BaseConfig.global_config().SQLITE_SQLALCHEMY if orm_config is None else orm_config
        super().__init__(configs)

    @override
    def _create_async_session_manager(self, configs: SqliteSQLAlchemyConfig) -> AsyncSqliteSQlAlchemySessionManager:
        """Create an async SQLite-specific session manager.

        Args:
            configs: SQLite configuration.

        Returns:
            An async SQLite session manager instance.
        """
        return AsyncSqliteSQlAlchemySessionManager(configs)
