from typing import Optional

from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)

from app.core.delete.user.workflow import DeleteUserWorkflow

from app.logs.setup_logger import LoggerManager, LOGGER


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

        self.logger.log_debug(
            f"[service] request dto: {request.__class__.__name__}"
        )

        result = await self.workflow.run(request)

        self.logger.log_debug(
            f"[service] workflow response: {result}"
        )

        deleted_user_id = None

        if result.get("data"):
            deleted_user_id = result["data"].get("deleted_user_id")

        return DeleteUserResponseDTO(
            success=result.get("success", False),
            message=result.get("message"),
            deleted_user_id=deleted_user_id,
        )