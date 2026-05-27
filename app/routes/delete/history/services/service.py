from typing import Optional

from app.core.delete.history.workflow import DeleteHistoryWorkflow
from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.delete.history.dtos.dto import (
    DeleteHistoryResponseDTO,
)


class DeleteHistoryService:
    """
    Service responsible for handling chat history deletion use cases.

    This class receives the authenticated user context, delegates
    execution to the workflow layer, and converts workflow results
    into standardized response DTOs.

    Attributes:
        workflow (DeleteHistoryWorkflow): Workflow responsible for
            delete history rules and execution.
        logger (LoggerManager): Logger instance for service events
            and errors.
    """

    def __init__(
        self,
        workflow: Optional[DeleteHistoryWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initializes the delete history service.

        Args:
            workflow (Optional[DeleteHistoryWorkflow]): Workflow
                responsible for delete history execution.
            logger (Optional[LoggerManager]): Logger instance used
                for service events and errors.
        """

        self.workflow = workflow or DeleteHistoryWorkflow()
        self.logger = logger or LOGGER

    async def handle_delete(
        self,
        current_user: UserTable,
    ) -> DeleteHistoryResponseDTO:
        """
        Handles the oldest chat history deletion process.

        Args:
            current_user (UserTable): Authenticated user requesting
                the delete history operation.

        Returns:
            DeleteHistoryResponseDTO:
                Standardized response DTO.
        """

        self.logger.log_info("[service] processing delete history request")

        self.logger.log_debug(f"[service] authenticated user id: {current_user.id}")

        result = await self.workflow.run(current_user)

        self.logger.log_debug(f"[service] workflow response: {result}")

        return DeleteHistoryResponseDTO(
            success=result.get("success", False),
            message=result.get("message"),
            data=result.get("data"),
        )
