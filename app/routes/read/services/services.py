from typing import Optional

from app.core.read.workflow import ReadUserWorkflow

from app.models.users_table import UserTable
from app.routes.read.dtos.dto import (
    GetUserRequestDTO,
    GetUserResponseDTO,
)

from app.logs.setup_logger import (
    LoggerManager,
    LOGGER,
)

class ReadUserService:
    """
    Service responsible for orchestrating
    the user read process.

    This class acts as the intermediary
    between the controller and workflow layers,
    handling business orchestration and converting
    workflow results into response DTOs.

    Attributes:
        workflow (ReadUserWorkflow):
            Workflow responsible for user read logic.

        logger (LoggerManager):
            Logger instance used for service logs.
    """

    def __init__(
        self,
        workflow: Optional[ReadUserWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:

        self.workflow = workflow or ReadUserWorkflow()

        self.logger = logger or LOGGER

    async def handle_read(
        self,
        request: GetUserRequestDTO,
        current_user: UserTable,
    ) -> GetUserResponseDTO:
        """
        Handles the user read request.

        Delegates the request to the workflow layer,
        receives the workflow result,
        and converts it into a response DTO.

        Args:
            request (GetUserRequestDTO):
                DTO containing user read filters.

        Returns:
            GetUserResponseDTO:
                Standardized response DTO containing
                operation result and user data.
        """

        self.logger.log_info(
            "[service] processing read user request"
        )

        self.logger.log_debug(
            f"[service] request dto: "
            f"{request.__class__.__name__}"
        )

        result = await self.workflow.run(
            request=request,
            current_user=current_user,            
        )

        self.logger.log_debug(
            f"[service] workflow response: {result}"
        )

        return GetUserResponseDTO(**result)
