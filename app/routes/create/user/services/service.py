from typing import Optional

from app.routes.create.user.dtos.dto import CreateUserRequestDTO, CreateUserResponseDTO
from app.core.create.user.workflow import CreateUserWorkflow
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateUserService:
    """
    Service layer responsible for handling user creation business logic.

    This class processes user creation requests, coordinating with the workflow layer
    and converting workflow dictionaries into response DTOs.

    Attributes:
        workflow (CreateUserWorkflow): Workflow instance used to process user creation logic.
        logger (LoggerManager): Logger instance for logging service events and errors.
    """

    def __init__(
        self,
        workflow: Optional[CreateUserWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.workflow = workflow or CreateUserWorkflow()
        self.logger = logger or LOGGER

    async def handle_create(
        self, request: CreateUserRequestDTO
    ) -> CreateUserResponseDTO:
        """
        Handles the user creation process by invoking the workflow.

        Args:
            request (CreateUserRequestDTO): DTO containing the user creation request data.

        Returns:
            CreateUserResponseDTO: Response DTO indicating success, failure, or error details.

        Raises:
            Exception: Propagates workflow errors to the controller boundary.
        """
        self.logger.log_info("[service] processing create user request")
        self.logger.log_debug(f"[service] request dto: {request.__class__.__name__}")
        result = await self.workflow.run(request)
        self.logger.log_debug(f"[service] response: {result}")
        return CreateUserResponseDTO(**result)
