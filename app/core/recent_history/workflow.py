from typing import Optional

from app.database.repository import DatabaseRepository
from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.history_table import HistoryTable


class RecentHistoryWorkflow:
    """
    Workflow responsible for orchestrating
    recent history retrieval operations.

    This workflow coordinates the retrieval
    of recent conversation history entries
    for authenticated users by delegating
    database access operations to the
    repository layer.

    The workflow also centralizes business
    rules related to:
    - user-based history filtering
    - result ordering
    - result limiting

    Attributes:
        logger (LoggerManager):
            Logger instance used to register
            workflow execution events and errors.

        history_repository (DatabaseRepository):
            Repository configured to operate
            on the HistoryTable model.
    """

    def __init__(
        self,
        history_repository: Optional[DatabaseRepository] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initialize workflow dependencies.

        Args:
            history_repository:
                Optional repository instance
                configured for history operations.

            logger:
                Optional logger instance used
                for structured workflow logging.
        """

        self.logger = logger or LOGGER

        self.history_repository = history_repository or DatabaseRepository(
            model=HistoryTable
        )

    async def execute(
        self,
        user_id: int,
        limit: int = 5,
    ):
        """
        Retrieve recent history entries
        for a specific authenticated user.

        This method applies the recent
        history retrieval workflow by
        delegating database access to the
        repository layer and enforcing
        retrieval constraints such as:
        - filtering by authenticated user
        - limiting the number of entries
        - ordering by creation date

        Args:
            user_id:
                Authenticated user identifier
                used to filter history entries.

            limit:
                Maximum number of recent
                history entries to retrieve.

        Returns:
            list[HistoryTable]:
                List containing the user's
                most recent history entries
                ordered by creation date
                in descending order.
        """

        self.logger.log_info(f"[workflow] retrieving recent history for user {user_id}")

        history_entries = (
            await self.history_repository.get_recent_history_by_user_id(
                user_id=user_id,
                limit=limit,
            )
        ) or []

        self.logger.log_info(
            f"[workflow] retrieved {len(history_entries)} recent history entries"
        )

        return history_entries
