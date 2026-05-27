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

    async def search_user_by_filters(
        self,
        id: Optional[int] = None,
        email: Optional[str] = None,
        cpf: Optional[str] = None,
    ) -> Optional[UserTable]:
        """
        Search for a user using one or more identifier filters.

        The query applies only the filters provided in the request
        and returns the first matching user when found.

        Args:
            id:
                Optional user ID filter.
            email:
                Optional user email filter.
            cpf:
                Optional user CPF filter.

        Returns:
            Optional[UserTable]:
                The matching user instance if found,
                otherwise None.
        """

        self.logger.log_info("[database] searching user with dynamic filters")

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = select(self.model)

                if id is not None:
                    query = query.where(self.model.id == id)

                elif email is not None:
                    query = query.where(self.model.email == email)

                elif cpf is not None:
                    query = query.where(self.model.cpf == cpf)

                result = await session.execute(query)

                user = result.scalar_one_or_none()

                self.logger.log_debug(f"[database] dynamic search result: {user}")

                return user

            except SQLAlchemyError as e:
                self.logger.log_error(
                    f"[database] error searching user dynamically: {e}"
                )

                return None

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

    async def update_user(
        self,
        user: UserTable,
        update_data: dict,
    ) -> Optional[int]:
        """
        Updates the provided user instance with validated fields.

        Applies the received update data to the target user,
        persists the changes in the database, and returns the
        updated user ID when the operation succeeds.

        Args:
            user (UserTable):
                Target user instance to be updated.
            update_data (dict):
                Dictionary containing validated fields to update.

        Returns:
            Optional[int]:
                The updated user ID if the operation succeeds,
                otherwise None.
        """

        self.logger.log_info(f"[database] updating user {user.id}")

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                db_user = await session.get(self.model, user.id)

                if not db_user:
                    self.logger.log_info("[database] user not found for update")

                    return None

                for field, value in update_data.items():
                    setattr(db_user, field, value)

                await session.commit()
                await session.refresh(db_user)

                self.logger.log_info(f"[database] user {user.id} updated successfully")

                return db_user.id

            except SQLAlchemyError as e:
                await session.rollback()

                self.logger.log_error(f"[database] error updating user: {e}")

                return None

    async def delete_user(self, filters: dict) -> Optional[T]:
        """
        Deletes a user using dynamic filter criteria.

        Applies the provided filters to locate the target user,
        performs the delete operation, and returns the deleted
        entity when the operation succeeds.

        Args:
            filters (dict): Dictionary containing dynamic search
                filters used to locate the user.

        Returns:
            Optional[T]: Deleted entity instance when found and
                successfully deleted, otherwise None.
        """

        self.logger.log_info(f"[database] deleting user with filters: {filters}")

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = select(self.model)

                for field, value in filters.items():
                    query = query.where(getattr(self.model, field) == value)

                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    self.logger.log_info("[database] delete_user: user not found")
                    return None

                deleted_user_id = user.id

                await session.delete(user)
                await session.commit()

                self.logger.log_info(
                    f"[database] user deleted successfully: " f"{deleted_user_id}"
                )

                return user

            except SQLAlchemyError as e:
                await session.rollback()

                self.logger.log_error(f"[database] error deleting user: {e}")

                return None

    async def delete_oldest_chat_history_by_user_id(
        self,
        user_id: int,
    ) -> Optional[T]:
        """
        Deletes the oldest chat history record for a specific user.

        Searches for the oldest chat history entry associated with the
        provided user ID, deletes the record safely, and returns the
        deleted entity when the operation succeeds.

        Args:
            user_id (int):
                Identifier of the user who owns the chat history.

        Returns:
            Optional[T]:
                Deleted chat history entity when found and successfully
                deleted, otherwise None.
        """

        self.logger.log_info(
            f"[database] deleting oldest chat history for user {user_id}"
        )

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = (
                    select(self.model)
                    .where(self.model.user_id == user_id)
                    .order_by(self.model.created_at.asc())
                )

                result = await session.execute(query)

                history = result.scalars().first()

                if not history:
                    self.logger.log_info(
                        "[database] no chat history found for deletion"
                    )

                    return None

                deleted_history_id = history.id

                await session.delete(history)
                await session.commit()

                self.logger.log_info(
                    "[database] oldest chat history deleted successfully: "
                    f"{deleted_history_id}"
                )

                return history

            except SQLAlchemyError as e:
                await session.rollback()

                self.logger.log_error(f"[database] error deleting chat history: {e}")

                return None

    async def get_recent_history_by_user_id(
        self,
        user_id: int,
        limit: int = 5,
    ):
        """
        Retrieve recent history entries
        for a specific authenticated user.

        This method filters history records
        by user identifier, orders results
        by creation date in descending order,
        and limits the number of returned entries.

        Args:
            user_id:
                Authenticated user identifier used
                to filter history entries.

            limit:
                Maximum number of recent history
                entries to retrieve.

        Returns:
            list[T]:
                List containing the user's most
                    recent history entries ordered
                from newest to oldest.
        """

        self.logger.log_info(f"[database] retrieving recent history for user {user_id}")

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = (
                    select(self.model)
                    .where(self.model.user_id == user_id)
                    .order_by(self.model.created_at.desc())
                    .limit(limit)
                )

                result = await session.execute(query)

                history_entries = result.scalars().all()

                self.logger.log_info(
                    f"[database] retrieved {len(history_entries)} recent history entries"
                )

                return history_entries

            except SQLAlchemyError as e:
                self.logger.log_error(
                    f"[database] error retrieving recent history: {e}"
                )

                return []

    async def read_user(
        self,
        filters: dict,
    ) -> Optional[List[T]]:
        """
        Retrieves users using dynamic filters.

        Args:
            filters (dict):
                Dictionary containing query filters.

        Returns:
            Optional[List[T]]:
                List of users found or None.
        """

        self.logger.log_info(f"[database] reading users with filters: {filters}")

        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = select(self.model)

                for field, value in filters.items():
                    query = query.where(getattr(self.model, field) == value)

                result = await session.execute(query)

                users = result.scalars().all()

                self.logger.log_debug(f"[database] ReadUser result count: {len(users)}")

                return users

            except SQLAlchemyError as e:
                self.logger.log_error(f"[database] error reading users: {e}")

                return None
