from typing import Optional

from app.database.repository import DatabaseRepository

from app.logs.setup_logger import LOGGER, LoggerManager

from app.models.history_table import (
    HistoryTable,
    HistoryStatus,
)

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
)

from app.models.users_table import UserTable


class SaveHistoryWorkflow:
    """
    Coordinates history creation or atomic session updates by building
    the history entity, persisting it through the repository,
    and returning the operation result.

    Dependencies:
        - DatabaseRepository: Handles history persistence.
        - LoggerManager: Provides workflow logging.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository] = None,
        logger: Optional[LoggerManager] = None,
    ):
        """
        Initializes workflow dependencies.

        Args:
            repository (Optional[DatabaseRepository]):
                Repository used for history persistence.

            logger (Optional[LoggerManager]):
                Logger instance used for workflow logs.
        """

        self.logger = logger or LOGGER

        self.repository = repository or DatabaseRepository(model=HistoryTable)

    async def execute(
        self,
        request: SaveHistoryRequestDTO,
        current_user: UserTable,
    ):
        """
        Creates history or atomically updates a saved session
        for the authenticated user.

        Args:
            request (SaveHistoryRequestDTO):
                DTO containing history data and an optional session identifier.

            current_user (UserTable):
                Authenticated user performing the request.

        Returns:
            dict:
                Operation result containing
                save status and the saved history identifier.
                Database failures produce an unsuccessful result.

        Raises:
            DeletedHistoryError:
                If the requested session belongs to a deleted history.
        """

        history = HistoryTable(
            user_id=current_user.id,
            session_id=request.session_id,
            dataset_id=request.dataset_id,
            title=request.title,
            message=request.message,
            status=HistoryStatus.ACTIVE,
        )

        history_id = await self.repository.save_history(history)

        if history_id is None:
            return {
                "success": False,
                "message": "Failed to save history.",
                "data": {
                    "history_id": history_id,
                },
            }

        return {
            "success": True,
            "message": "History saved successfully.",
            "data": {
                "history_id": history_id,
            },
        }
