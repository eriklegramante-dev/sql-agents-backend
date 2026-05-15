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
    response DTO containing the update operation result.

    Attributes:
        workflow (UpdateUserWorkflow): Workflow instance for executing update logic.
    logger (LoggerManager):
        Logger for service events and errors.

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
        Handles the execution of the user update operation.

        Receives validated update request data from the controller layer,
        delegates the update process to the workflow layer, and returns
        a standardized response DTO containing the operation result.

        Args:
            request (UpdateUserRequestDTO):
                DTO containing validated user update data.

        Returns:
            UpdateUserResponseDTO:
                Standardized response containing the update operation result.
        """
        self.logger.log_info("[service] processing update user request")

        result = await self.workflow.run(request)

        return UpdateUserResponseDTO(**result)
