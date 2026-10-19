from typing import Protocol


class ChatSessionCountRepository(Protocol):
    """Define the repository operations required for session counting."""

    async def count_sessions_by_user_id(self, user_id: int) -> int:
        """Return the user's non-deleted saved session total."""
        ...