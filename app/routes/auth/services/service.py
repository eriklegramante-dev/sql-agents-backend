from typing import Optional

from app.routes.auth.dtos.dto import LoginRequestDTO, LoginResponseDTO
from app.core.auth.workflow import LoginWorkflow
from app.logs.setup_logger import LoggerManager, LOGGER


class LoginService:
    """
    Service layer responsible for handling user authentication logic.

    This class processes login requests by coordinating with the workflow layer
    and converting workflow dictionaries into response DTOs.

    Attributes:
        workflow (LoginWorkflow): Workflow instance used to process authentication logic.
        logger (LoggerManager): Logger instance for logging service events and errors.
    """

    def __init__(
        self,
        workflow: Optional[LoginWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.workflow = workflow or LoginWorkflow()
        self.logger = logger or LOGGER

    async def handle_login(self, request: LoginRequestDTO) -> LoginResponseDTO:
        """
        Handles the authentication process by invoking the workflow.

        Args:
            request (LoginRequestDTO): DTO containing the login request data.

        Returns:
            LoginResponseDTO: Response DTO indicating authentication success or failure.
        """
        self.logger.log_info("[service] authentication process started")
        self.logger.log_debug(f"[service] login username: {request.username}")
        result = await self.workflow.run(request)
        self.logger.log_debug(f"[service] login success: {result.get('success')}")
        return LoginResponseDTO(**result)
