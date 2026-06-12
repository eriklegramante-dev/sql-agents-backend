from typing import Optional

from app.logs.setup_logger import LOGGER, LoggerManager

from app.core.save_history.workflow import SaveHistoryWorkflow

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
    SaveHistoryResponseDTO,
)

from app.models.users_table import UserTable


class SaveHistoryService:
    """
    Service responsible for
    history save operations.
    """

    def __init__(
        self,
        workflow: Optional[SaveHistoryWorkflow] = None,
        logger: Optional[LoggerManager] = None,
    ):
        """
        Initializes service dependencies.

        Args:
            workflow (Optional[SaveHistoryWorkflow]):
                Workflow used for
                history save operations.

            logger (Optional[LoggerManager]):
                Logger instance used
                for service logs.
        """

        self.logger = logger or LOGGER
        self.workflow = workflow or SaveHistoryWorkflow()

    async def handle_save_history(
        self,
        request: SaveHistoryRequestDTO,
        current_user: UserTable,
    ) -> SaveHistoryResponseDTO:
        """
        Processes the history save request.

        Args:
            request (SaveHistoryRequestDTO):
                DTO containing history data.

            current_user (UserTable):
                Authenticated user performing
                the request.

        Returns:
            SaveHistoryResponseDTO:
                Operation result containing
                the saved history data.
        """

        result = await self.workflow.execute(
            request=request,
            current_user=current_user,
        )

        return SaveHistoryResponseDTO(**result)
