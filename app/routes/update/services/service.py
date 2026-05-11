from typing import Optional

from app.core.update.workflow import UpdateUserWorkflow
from app.logs.setup_logger import LOGGER, LoggerManager
from app.routes.update.dtos.dto import (
    UpdateUserRequestDTO,
    UpdateUserResponseDTO,
)


class UpdateUserService:
    """
    Handles user update orchestration.
    """

    def __init__(
        self,
        workflow: Optional[UpdateUserWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.workflow = workflow or UpdateUserWorkflow()
        self.logger = logger or LOGGER

    async def handle_update(
        self,
        request: UpdateUserRequestDTO,
    ) -> UpdateUserResponseDTO:
        """
        Delegates update execution to the workflow layer.
        """
        self.logger.log_info(
            "[service] processing update user request"
        )

        result = await self.workflow.run(request)

        return UpdateUserResponseDTO(**result)