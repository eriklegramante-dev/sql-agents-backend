from typing import Optional

from app.routes.create.admin.dtos.dto import (
    CreateAdminRequestDTO,
    CreateAdminResponseDTO,
)
from app.core.create.admin.workflow import CreateAdminWorkflow
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateAdminService:
    """
    Service responsible for orchestrating the admin user creation process.

    This class serves as the intermediary between the controller and the workflow,
    handling business logic and converting workflow dictionaries into response DTOs.

    Attributes:
        workflow (CreateAdminWorkflow): Workflow instance responsible for user creation logic.
        logger (LoggerManager): Logger instance for recording workflow actions.
    """

    def __init__(
        self,
        workflow: Optional[CreateAdminWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.workflow = workflow or CreateAdminWorkflow()
        self.logger = logger or LOGGER

    async def handle_create(
        self, request: CreateAdminRequestDTO
    ) -> CreateAdminResponseDTO:
        """
        Handles the business logic for admin user creation.

        Processes the request, delegates execution to the workflow layer,
        and wraps the result into a response DTO.

        Args:
            request (CreateAdminRequestDTO): The DTO containing admin creation data.

        Returns:
            CreateAdminResponseDTO: DTO containing the operation result, success flag,
                message, and additional data (created user ID or error details).

        Raises:
            Exception: Propagates workflow errors to the controller boundary.
        """
        self.logger.log_info("[service] processing create admin request")
        self.logger.log_debug(f"[service] request dto: {request.__class__.__name__}")
        result = await self.workflow.run(request)
        self.logger.log_debug(f"[service] response: {result}")
        return CreateAdminResponseDTO(**result)
