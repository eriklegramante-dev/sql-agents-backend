from typing import Optional, TypeVar, Generic, Type, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from app.database.connection import DatabaseConnection
from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import Base, UserTable

T = TypeVar("T")


class DatabaseRepository(Generic[T]):
    """
    Generic repository class for handling asynchronous database operations.

    Provides CRUD operations for any SQLAlchemy model, with support for logging and
    customizable database connections and models.

    Attributes:
        logger (LoggerManager): Logger instance for recording database events and errors.
        db_connection (DatabaseConnection): Manages the async database engine and sessionmaker.
        model (Type[T]): The SQLAlchemy model class this repository operates on.
    """

    def __init__(
            self,
            db_connection: Optional[DatabaseConnection] = None,
            logger: Optional[LoggerManager] = None,
            model: Optional[Type[T]] = None,
    ) -> None:
        self.logger = logger or LOGGER
        self.db_connection = db_connection or DatabaseConnection(logger=self.logger)
        self.model = model or UserTable

    async def create_tables(self) -> bool:
        """
        Asynchronously creates all database tables defined in the model's metadata.

        Returns:
            bool: True if tables were created successfully, False otherwise.
        """
        self.logger.log_info("[database] creating all tables")
        try:
            async with self.db_connection.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                self.logger.log_info("[database] all tables created successfully")
                return True

        except SQLAlchemyError as e:
            self.logger.log_error(f"[database] error creating tables: {e}")
            return False

    async def insert(self, instance: T) -> Optional[int]:
        """
        Inserts a new record into the database.

        Args:
            instance (T): An instance of the model to be inserted.

        Returns:
            Optional[int]: The ID of the newly inserted record, or None if insertion fails.
        """
        self.logger.log_info("[database] inserting record")
        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                session: AsyncSession
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                record_id = getattr(instance, "id", None)
                self.logger.log_info(f"[database] record inserted. id: {record_id}")
                return record_id

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.log_error(f"[database] error inserting record: {e}")
                return None

    async def get_by_id(self, record_id: int) -> Optional[T]:
        """
        Retrieves a record by its primary key.

        Args:
            record_id (int): The primary key ID of the record to retrieve.

        Returns:
            Optional[T]: The record instance if found, otherwise None.
        """
        self.logger.log_info(f"[database] retrieving record by id: {record_id}")
        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                result = await session.get(self.model, record_id)
                self.logger.log_debug(f"[database] get_by_id result: {result}")
                return result

            except SQLAlchemyError as e:
                self.logger.log_error(f"[database] error retrieving record: {e}")
                return None

    async def get_user_by_email(self, email: str) -> Optional[UserTable]:
        """
        Retrieves a user record by its email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            Optional[UserTable]: The user instance if found, otherwise None.
        """
        self.logger.log_info(f"[database] retrieving user by email: {email}")
        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            result = await session.execute(
                select(self.model).where(self.model.email == email)
            )
            user = result.scalar_one_or_none()
            self.logger.log_debug(f"[database] get_user_by_email result: {user}")
            return user

    async def update_last_login_at(self, user_id: int) -> bool:
        """
        Updates the last_login_at field for a user after successful authentication.

        Args:
            user_id (int): The user's ID.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        self.logger.log_info(f"[database] updating last_login_at for user {user_id}")
        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                user = await session.get(self.model, user_id)
                if not user:
                    self.logger.log_debug(
                        "[database] update_last_login_at: user not found"
                    )
                    return False
                user.last_login_at = datetime.utcnow()
                await session.commit()
                self.logger.log_info(
                    f"[database] last_login_at updated for user {user_id}"
                )
                return True

            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.log_error(f"[database] error updating last_login_at: {e}")
                return False

    async def delete_user(self, filters: dict) -> Optional[T]:
        """
        Deletes a user using dynamic filters.

        Args:
            filters (dict):
                Dynamic filters such as id, email, or cpf.

        Returns:
            Optional[T]:
                Deleted user instance if successful, otherwise None.
        """

        self.logger.log_info(
            f"[database] deleting user with filters: {filters}"
        )

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = select(self.model)

                for field, value in filters.items():
                    query = query.where(
                        getattr(self.model, field) == value
                    )

                result = await session.execute(query)

                user = result.scalar_one_or_none()

                if not user:
                    self.logger.log_info(
                        "[database] delete_user: user not found"
                    )
                    return None

                deleted_user_id = user.id

                await session.delete(user)
                await session.commit()

                self.logger.log_info(
                    f"[database] user deleted successfully: {deleted_user_id}"
                )

                return user

            except SQLAlchemyError as e:
                await session.rollback()

                self.logger.log_error(
                    f"[database] error deleting user: {e}"
                )

                return None


