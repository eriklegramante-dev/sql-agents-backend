from typing import Any, Dict, Optional

from app.database.repository import DatabaseRepository
from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.chat_history_table import ChatHistoryTable
from app.models.users_table import UserTable


class DeleteHistoryWorkflow:
    """
    Workflow responsible for orchestrating the chat history deletion process.

    This class identifies the oldest chat history record owned by the
    authenticated user, delegates the delete operation to the repository,
    and returns a standardized response.

    Attributes:
        repository (DatabaseRepository[ChatHistoryTable]):
            Repository responsible for chat history database operations.
        logger (LoggerManager):
            Logger instance used to register workflow events.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[ChatHistoryTable]] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initializes the delete history workflow.

        Args:
            repository (Optional[DatabaseRepository[ChatHistoryTable]]):
                Repository used to execute chat history database operations.
            logger (Optional[LoggerManager]):
                Logger instance used to register workflow events.
        """

        self.repository = repository or DatabaseRepository(model=ChatHistoryTable)
        self.logger = logger or LOGGER

    async def run(self, current_user: UserTable) -> Dict[str, Any]:
        """
        Executes the oldest chat history deletion workflow.

        Args:
            current_user (UserTable):
                Authenticated user requesting the history deletion.

        Returns:
            Dict[str, Any]:
                Standardized workflow response containing the operation
                status and deleted chat history information.
        """

        self.logger.log_info("[workflow] processing delete history")
        self.logger.log_debug(f"[workflow] authenticated user id: {current_user.id}")

        deleted_history = await self.repository.delete_oldest_chat_history_by_user_id(
            user_id=current_user.id,
        )

        if not deleted_history:
            self.logger.log_info("[workflow] chat history not found")

            return {
                "success": False,
                "message": "Chat history not found or could not be deleted.",
                "data": None,
            }

        self.logger.log_info("[workflow] chat history deleted successfully")

        return {
            "success": True,
            "message": "Chat history deleted successfully.",
            "data": {
                "deleted_history_id": deleted_history.id,
            },
        }
