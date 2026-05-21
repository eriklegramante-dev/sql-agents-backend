from typing import Optional

from app.core.delete.user.workflow import DeleteUserWorkflow
from app.logs.setup_logger import LOGGER, LoggerManager
from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)


class DeleteUserService:
    """
    Service responsible for handling user deletion use cases.

    This class receives validated delete requests, delegates execution
    to the workflow layer, and converts workflow results into
    standardized response DTOs.

    Attributes:
        workflow (DeleteUserWorkflow): Workflow responsible for user
            deletion rules and execution.
        logger (LoggerManager): Logger instance for service events
            and errors.
    """

    def __init__(
        self,
        workflow: Optional[DeleteUserWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.workflow = workflow or DeleteUserWorkflow()
        self.logger = logger or LOGGER

    async def handle_delete(
        self,
        request: DeleteUserRequestDTO,
    ) -> DeleteUserResponseDTO:
        """
        Handles the user deletion process.

        Args:
            request (DeleteUserRequestDTO):
                DTO containing delete identifiers.

        Returns:
            DeleteUserResponseDTO:
                Standardized response DTO.
        """

        self.logger.log_info("[service] processing delete user request")

        self.logger.log_debug(f"[service] request dto: {request.__class__.__name__}")

        result = await self.workflow.run(request)

        self.logger.log_debug(f"[service] workflow response: {result}")

        return DeleteUserResponseDTO(
            success=result.get("success", False),
            message=result.get("message"),
            data=result.get("data"),
        )
