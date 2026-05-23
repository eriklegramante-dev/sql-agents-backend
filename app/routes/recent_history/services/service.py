from typing import Optional

from app.core.recent_history.workflow import RecentHistoryWorkflow
from app.logs.setup_logger import LOGGER, LoggerManager
from app.routes.recent_history.dtos.dto import (
    RecentHistoryItemDTO,
    RecentHistoryResponseDTO,
)


class RecentHistoryService:
    """
    Service responsible for handling recent history retrieval operations.

    This service coordinates the communication between the
    controller layer and the workflow layer, converts database
    models into response DTOs, and returns standardized
    response structures for frontend consumption.

    Attributes:
        logger (LoggerManager):
            Logger instance used to register service events and errors.
        workflow (RecentHistoryWorkflow):
            Workflow responsible for recent history business logic.
    """

    def __init__(
        self,
        workflow: Optional[RecentHistoryWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initialize service dependencies.

        Args:
            workflow:
                Optional workflow instance for dependency injection.
            logger:
                Optional logger instance for structured logging.
        """
        self.logger = logger or LOGGER
        self.workflow = workflow or RecentHistoryWorkflow()

    async def handle_recent_history(
        self,
        user_id: int,
    ) -> RecentHistoryResponseDTO:
        """
        Retrieve and format recent history entries
        for the authenticated user.

        This method delegates the retrieval process to the
        workflow layer, converts the resulting database models
        into DTO objects, and returns a standardized response DTO.

        Args:
            user_id:
                Authenticated user identifier used to retrieve
                recent history entries.

        Returns:
            RecentHistoryResponseDTO:
                Standardized response containing the user's
                recent history entries.
        """
        try:
            self.logger.log_info(
                f"[service] retrieving recent history for user {user_id}"
            )

            history_entries = await self.workflow.execute(
                user_id=user_id,
            )

            data = [
                RecentHistoryItemDTO(
                    id=history.id,
                    dataset_id=history.dataset_id,
                    title=history.title,
                    status=history.status.value,
                    created_at=history.created_at,
                    updated_at=history.updated_at,
                )
                for history in history_entries
            ]

            self.logger.log_info(
                f"[service] recent history retrieved successfully for user {user_id}"
            )

            return RecentHistoryResponseDTO(
                success=True,
                message="Recent history retrieved successfully.",
                data=data,
            )

        except Exception as e:
            self.logger.log_error(
                f"[service] error retrieving recent history: {str(e)}"
            )

            return RecentHistoryResponseDTO(
                success=False,
                message="Failed to retrieve recent history.",
                data=[],
            )
