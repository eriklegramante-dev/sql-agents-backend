from typing import Any, Dict, Optional

from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
)
from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable
from app.logs.setup_logger import LoggerManager, LOGGER


class DeleteUserWorkflow:
    """
    Workflow responsible for orchestrating the user deletion process.

    This class validates delete filters, interacts with the repository,
    and returns standardized responses.

    Attributes:
        repository (DatabaseRepository[UserTable]):
            Repository responsible for database operations.

        logger (LoggerManager):
            Logger instance for workflow events.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[UserTable]] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.repository = repository or DatabaseRepository(model=UserTable)
        self.logger = logger or LOGGER

    async def run(self, request: DeleteUserRequestDTO) -> Dict[str, Any]:
        """
        Executes the user deletion workflow.

        Args:
            request (DeleteUserRequestDTO):
                DTO containing delete filters.

        Returns:
            Dict[str, Any]:
                Standardized workflow response.
        """

        self.logger.log_info("[workflow] processing delete user")
        self.logger.log_debug(f"[workflow] request dto: {request.__class__.__name__}")

        filters = {}

        if request.id:
            filters["id"] = request.id

        if request.email:
            filters["email"] = request.email

        if request.cpf:
            filters["cpf"] = request.cpf

        self.logger.log_debug(f"[workflow] delete filters: {filters}")

        deleted_user = await self.repository.delete_user(filters)

        if not deleted_user:
            self.logger.log_info("[workflow] user not found")

            return {
                "success": False,
                "message": "User not found or could not be deleted.",
                "data": None,
            }

        self.logger.log_info("[workflow] user deleted successfully")

        return {
            "success": True,
            "message": "User deleted successfully.",
            "data": {"deleted_user_id": deleted_user.id},
        }
