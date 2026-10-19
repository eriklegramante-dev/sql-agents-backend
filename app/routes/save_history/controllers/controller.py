from typing import Optional

from fastapi.responses import JSONResponse

from app.database.history_errors import DeletedHistoryError

from app.logs.setup_logger import LOGGER, LoggerManager

from app.routes.save_history.services.service import (
    SaveHistoryService,
)

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
    SaveHistoryResponseDTO,
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
                Standardized response with HTTP 200 on success,
                HTTP 409 when the session history is deleted,
                or HTTP 500 when persistence fails.
        """

        try:
            response = await self.service.handle_save_history(
                request=request,
                current_user=current_user,
            )
        except DeletedHistoryError:
            return JSONResponse(
                status_code=409,
                content=SaveHistoryResponseDTO(
                    success=False,
                    message="Deleted history cannot be saved.",
                    data={"history_id": None},
                ).model_dump(mode="json"),
            )

        return JSONResponse(
            status_code=200 if response.success else 500,
            content=response.model_dump(mode="json"),
        )
