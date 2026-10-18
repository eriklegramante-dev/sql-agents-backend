from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.repository import DatabaseRepository
from app.models.history_table import HistoryTable, HistoryStatus


class HistorySessionRepository(DatabaseRepository[HistoryTable]):
    """
    Repository responsible for counting saved conversation sessions.

    Includes active and archived histories with a session identifier,
    excluding deleted histories and legacy records without a session.
    """

    async def count_sessions_by_user_id(self, user_id: int) -> int:
        """
        Count saved conversation sessions belonging to a specific user.

        Args:
            user_id (int):
                User identifier used to filter history records.

        Returns:
            int:
                Number of non-deleted histories with a session identifier.
                Returns zero when no matching sessions exist.

        Raises:
            SQLAlchemyError:
                If the database query fails, after logging the error.
        """
        sessionmaker = self.db_connection.get_session()

        async with sessionmaker() as session:
            try:
                query = (
                    select(func.count(HistoryTable.id))
                    .select_from(HistoryTable)
                    .where(
                        HistoryTable.user_id == user_id,
                        HistoryTable.session_id.is_not(None),
                        HistoryTable.status != HistoryStatus.DELETED,
                    )
                )

                result = await session.execute(query)

                return result.scalar_one()

            except SQLAlchemyError as error:
                self.logger.log_error(
                    f"[database] error counting history sessions: {error}"
                )
                raise