from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.settings.setting import get_settings, Settings
from app.logs.setup_logger import LOGGER, LoggerManager


class DatabaseConnection:
    """
    Manages asynchronous database connections using SQLAlchemy.

    This class is responsible for creating and maintaining the asynchronous database engine
    and sessionmaker, as well as handling proper resource cleanup.

    Attributes:
        logger (LoggerManager): Logger instance for recording database connection events.
        settings (Settings): Application settings containing database configuration.
        engine: The asynchronous SQLAlchemy engine instance.
        sessionmaker: The async sessionmaker bound to the engine for creating sessions.
    """

    def __init__(
        self,
        logger: Optional[LoggerManager] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self.logger = logger or LOGGER
        self.settings = settings or get_settings()
        self.logger.log_info("[database] initializing async engine")
        self.engine = create_async_engine(
            self.settings.database.get_current_url(),
            echo=False,
            future=True,
        )
        self.logger.log_debug(
            f"[database] async engine created with url: {self.settings.database.get_current_url()}"
        )
        self.sessionmaker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        self.logger.log_debug("[database] sessionmaker initialized")

    def get_session(self) -> async_sessionmaker[AsyncSession]:
        """
        Retrieves the asynchronous sessionmaker for database operations.

        Returns:
            async_sessionmaker[AsyncSession]: The sessionmaker instance to create async database sessions.
        """
        self.logger.log_debug("[database] get_session called")
        return self.sessionmaker

    async def close(self) -> None:
        """
        Disposes of the asynchronous database engine, releasing resources.

        Logs the disposal process for audit and debugging purposes.

        Returns:
            None
        """
        self.logger.log_info("[database] Disposing async engine...")
        await self.engine.dispose()
        self.logger.log_info("[database] Engine disposed.")
