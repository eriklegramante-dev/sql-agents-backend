from typing import Optional

from fastapi.responses import JSONResponse

from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.recent_history.dtos.dto import (
    RecentHistoryResponseDTO,
)
from app.routes.recent_history.services.service import (
    RecentHistoryService,
)


class RecentHistoryController:
    """
    Controller responsible for handling recent history retrieval requests.

    This controller validates request context information,
    delegates the recent history retrieval process to the
    service layer, and returns standardized HTTP responses
    for frontend consumption.

    Attributes:
        logger (LoggerManager):
            Logger instance used to register controller events and errors.
        service (RecentHistoryService):
            Service responsible for handling recent history business flow.
    """

    def __init__(
        self,
        service: Optional[RecentHistoryService] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initialize controller dependencies.

        Args:
            service:
                Optional service instance for dependency injection.
            logger:
                Optional logger instance for structured logging.
        """
        self.logger = logger or LOGGER
        self.service = service or RecentHistoryService()

    async def get_recent_history(
        self,
        current_user: UserTable,
    ) -> JSONResponse:
        """
        Retrieve the most recent history entries
        for the authenticated user.

        This method delegates the retrieval process to the
        service layer and formats the response into a
        standardized JSON structure.

        Args:
            current_user:
                Authenticated user performing the request.

        Returns:
            JSONResponse:
                Standardized HTTP response containing
                the user's recent history entries.
        """
        try:
            self.logger.log_info(
                f"[controller] retrieving recent history for user {current_user.id}"
            )

            response = await self.service.handle_recent_history(
                user_id=current_user.id,
            )

            return response

        except Exception as e:
            self.logger.log_error(
                f"[controller] internal error retrieving recent history: {str(e)}"
            )

            dto = RecentHistoryResponseDTO(
                success=False,
                message="Internal server error.",
                data=[],
            )

            return dto
