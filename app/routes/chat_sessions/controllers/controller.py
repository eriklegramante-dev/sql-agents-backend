from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.logs.setup_logger import LOGGER, LoggerManager
from app.routes.chat_sessions.dtos.dto import ChatSessionCountResponseDTO
from app.routes.chat_sessions.services.service import ChatSessionCountService


class ChatSessionCountController:
    """
    Controller responsible for handling saved session count requests.

    Converts service results and database failures into HTTP responses.

    Attributes:
        service (ChatSessionCountService):
            Service responsible for retrieving the session count.
        logger (LoggerManager):
            Logger instance used to register controller errors.
    """

    def __init__(
        self,
        service: ChatSessionCountService,
        logger: LoggerManager | None = None,
    ) -> None:
        """Initialize the controller dependencies.

        Args:
            service: Service responsible for retrieving the session count.
            logger: Optional logger used to register controller errors.
        """
        self.service = service
        self.logger = logger if logger is not None else LOGGER

    async def execute(self, user_id: int) -> JSONResponse:
        """
        Handle the authenticated user's session count request.

        Args:
            user_id (int):
                Authenticated user identifier used to filter sessions.

        Returns:
            JSONResponse:
                Standardized response with HTTP 200 and the session total,
                or HTTP 500 with null data when a database error occurs.
                Includes Cache-Control: no-store to prevent response caching.
        """
        try:
            response = await self.service.execute(user_id=user_id)
            status_code = 200

        except SQLAlchemyError:
            self.logger.log_error(
                "[controller] failed to count saved chat sessions"
            )

            response = ChatSessionCountResponseDTO(
                success=False,
                message="Failed to count chat sessions.",
                data=None,
            )
            status_code = 500

        return JSONResponse(
            status_code=status_code,
            content=response.model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )