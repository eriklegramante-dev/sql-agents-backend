"""Service layer for user update workflow execution."""

from typing import Optional

from app.core.update.workflow import UpdateUserWorkflow
from app.logs.setup_logger import LOGGER, LoggerManager
from app.routes.update.dtos.dto import (
    UpdateUserRequestDTO,
    UpdateUserResponseDTO,
)


class UpdateUserService:
    """
    Service responsible for handling user update use cases.

    This class receives validated update requests from the controller,
    delegates execution to the workflow layer, and returns a standardized
    response DTO.

    """

    def __init__(
        self,
        workflow: Optional[UpdateUserWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """Initialize update service dependencies."""
        self.workflow = workflow or UpdateUserWorkflow()
        self.logger = logger or LOGGER

    async def handle_update(
        self,
        request: UpdateUserRequestDTO,
    ) -> UpdateUserResponseDTO:
        """
        Handles the user update request through the workflow layer.

        Args:
            request (UpdateUserRequestDTO): Validated update request data.

        Returns:
            UpdateUserResponseDTO: Response containing the update operation result.
        """
        self.logger.log_info("[service] processing update user request")

        result = await self.workflow.run(request)

        return UpdateUserResponseDTO(**result)
