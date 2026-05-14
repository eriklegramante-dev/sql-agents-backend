"""User update workflow for locating users and applying valid profile changes."""

from typing import Any, Dict, Optional

from app.database.repository import DatabaseRepository
from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.update.dtos.dto import UpdateUserRequestDTO
from app.security.hashing import PasswordManager


class UpdateUserWorkflow:
    """
    Workflow responsible for updating users.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[UserTable]] = None,
        logger: Optional[LoggerManager] = None,
        password_manager: Optional[PasswordManager] = None,
    ) -> None:
        """Initialize update workflow dependencies with default services."""
        self.repository = repository or DatabaseRepository(model=UserTable)
        self.logger = logger or LOGGER
        self.password_manager = password_manager or PasswordManager()

    async def run(self, request: UpdateUserRequestDTO) -> Dict[str, Any]:
        """
        Executes the user update workflow.

        Args:
            request (UpdateUserRequestDTO): Validated update request data.

        Returns:
            Dict[str, Any]: Operation result containing success, message, and optional data.
        """
        self.logger.log_info("[workflow] processing user update")

        user = await self.repository.search_user_by_filters(
            id=request.id,
            email=request.email,
        )

        if not user:
            self.logger.log_info("[workflow] target user not found")

            return {
                "success": False,
                "message": "Target user not found.",
            }

        update_data = {}

        self.logger.log_debug(f"update_data: {update_data}")

        if request.email is not None:
            update_data["email"] = request.email

        if request.name is not None:
            update_data["name"] = request.name

        if request.role is not None:
            update_data["role"] = request.role

        if request.status is not None:
            update_data["status"] = request.status

        if request.password is not None:
            hashed_password = self.password_manager.hash_password(request.password)

            update_data["password"] = hashed_password

        if not update_data:
            return {
                "success": False,
                "message": "No valid update data provided.",
            }

        updated = await self.repository.update_user(
            user=user,
            update_data=update_data,
        )

        if not updated:
            return {
                "success": False,
                "message": "Failed to update user.",
            }

        self.logger.log_info(f"[workflow] user {user.id} updated successfully")

        return {
            "success": True,
            "message": "User updated successfully.",
            "data": {"id": user.id},
        }
