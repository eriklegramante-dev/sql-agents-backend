from app.core.chat_sessions.contracts import ChatSessionCountRepository


class ChatSessionCountWorkflow:
    """Coordinate saved session counting through an injected contract.

    Attributes:
        repository: Repository responsible for retrieving session totals.
    """

    def __init__(self, repository: ChatSessionCountRepository) -> None:
        """Initialize the workflow with its required repository.

        Args:
            repository: Implementation of the session counting contract.
        """
        self.repository = repository

    async def execute(self, user_id: int) -> int:
        """Retrieve the authenticated user's saved session total.

        Args:
            user_id: Authenticated user identifier used to filter sessions.

        Returns:
            Total non-deleted histories with a session identifier.

        Raises:
            Exception: Propagates failures from the injected repository.
        """
        return await self.repository.count_sessions_by_user_id(
            user_id=user_id,
        )