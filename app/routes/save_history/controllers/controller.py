from typing import Optional

from fastapi.responses import JSONResponse

from app.logs.setup_logger import LOGGER, LoggerManager

from app.routes.save_history.services.service import (
    SaveHistoryService,
)

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
)


class SaveHistoryController:
    """
    Controller responsible for
    handling history save requests.

    Attributes:
        service (SaveHistoryService):
            Service responsible for
            history save operations.

        logger (LoggerManager):
            Logger instance used for
            controller logs.
    """

    def __init__(
        self,
        service: Optional[SaveHistoryService] = None,
        logger: Optional[LoggerManager] = None,
    ):
        self.logger = logger or LOGGER
        self.service = service or SaveHistoryService()

    async def handle(
        self,
        request: SaveHistoryRequestDTO,
        current_user,
    ):
        """
        Handles the history save request.

        Args:
            request (SaveHistoryRequestDTO):
                DTO containing history data.

            current_user:
                Authenticated user performing
                the request.

        Returns:
            JSONResponse:
                Standardized API response.
        """

        response = await self.service.handle_save_history(
            request=request,
            current_user=current_user,
        )

        return JSONResponse(
            status_code=200,
            content=response.model_dump(mode="json"),
        )
