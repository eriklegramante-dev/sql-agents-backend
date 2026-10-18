from app.database.history_session_repository import HistorySessionRepository
from app.models.history_table import HistoryTable


class ChatSessionCountWorkflow:
    """
    Workflow responsible for coordinating saved session counting.

    Delegates retrieval of the user's non-deleted session total
    to the history session repository.

    Attributes:
        repository (HistorySessionRepository):
            Repository configured to count saved history sessions.
    """

    def __init__(
        self,
        repository: HistorySessionRepository | None = None,
    ) -> None:
        """
        Initialize workflow dependencies.

        Args:
            repository (HistorySessionRepository | None):
                Optional repository instance for dependency injection.
                Defaults to a repository configured for HistoryTable.
        """
        self.repository = (
            repository
            if repository is not None
            else HistorySessionRepository(model=HistoryTable)
        )

    async def execute(self, user_id: int) -> int:
        """
        Retrieve the saved session total for the authenticated user.

        Args:
            user_id (int):
                Authenticated user identifier used to filter sessions.

        Returns:
            int:
                Total active and archived histories with a session identifier.

        Raises:
            SQLAlchemyError:
                If the repository fails to retrieve the session total.
        """
        return await self.repository.count_sessions_by_user_id(
            user_id=user_id,
        )