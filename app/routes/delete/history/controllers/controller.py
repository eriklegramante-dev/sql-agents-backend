from typing import Optional

from fastapi.responses import JSONResponse

from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.delete.history.dtos.dto import DeleteHistoryResponseDTO
from app.routes.delete.history.services.service import DeleteHistoryService


class DeleteHistoryController:
    """
    Controller responsible for handling chat history deletion requests.

    This class validates the authenticated user context, delegates
    execution to the service layer, and returns standardized HTTP
    responses for the delete history flow.

    Attributes:
        service (DeleteHistoryService): Service responsible for
            delete history business logic.
        logger (LoggerManager): Logger instance for controller
            events and errors.
    """

    def __init__(
        self,
        service: Optional[DeleteHistoryService] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initializes the delete history controller.

        Args:
            service (Optional[DeleteHistoryService]): Service responsible
                for delete history business logic.
            logger (Optional[LoggerManager]): Logger instance used for
                controller events and errors.
        """

        self.service = service or DeleteHistoryService()
        self.logger = logger or LOGGER

    async def delete_history(
        self,
        current_user: UserTable,
    ) -> JSONResponse:
        """
        Deletes the oldest chat history record for the authenticated user.

        Args:
            current_user (UserTable): Authenticated user performing the
                delete history operation.

        Returns:
            JSONResponse: Standardized HTTP response containing the delete
                history operation result.
        """

        try:
            self.logger.log_info("[controller] delete history request received")

            if not current_user or not current_user.id:
                raise PermissionError("Authenticated user context is required.")

            response = await self.service.handle_delete(current_user)

            status_code = 200 if response.success else 404

            return JSONResponse(
                status_code=status_code,
                content=response.model_dump(),
            )

        except PermissionError as e:
            self.logger.log_error(str(e))

            dto = DeleteHistoryResponseDTO(
                success=False,
                message=str(e),
                data=None,
            )

            return JSONResponse(
                status_code=401,
                content=dto.model_dump(),
            )

        except Exception as e:
            self.logger.log_error(f"[controller] internal error: {str(e)}")

            dto = DeleteHistoryResponseDTO(
                success=False,
                message="Internal server error",
                data=None,
            )

            return JSONResponse(
                status_code=500,
                content=dto.model_dump(),
            )
