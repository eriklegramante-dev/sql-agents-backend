from typing import Any, Dict, Optional

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable, UserRole
from app.logs.setup_logger import LoggerManager, LOGGER
from app.routes.read.dtos.dto import GetUserRequestDTO


class ReadUserWorkflow:
    """
    Workflow responsible for orchestrating the user read process.

    This class handles user search requests, applies filters,
    communicates with the repository layer, validates query results,
    and returns a sanitized response containing only safe user data.

    Attributes:
        repository (ReadUserRepository):
            Repository responsible for database read operations.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[UserTable]] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """
        Initializes the read user workflow dependencies.

        Args:
            repository (Optional[DatabaseRepository[UserTable]]):
                Repository used for user database operations.

            logger (Optional[LoggerManager]):
                Logger instance used for workflow logs.
        """

        self.repository = repository or DatabaseRepository(model=UserTable)

        self.logger = logger or LOGGER

    async def run(
        self, request: GetUserRequestDTO, current_user: UserTable
    ) -> Dict[str, Any]:
        """
        Processes the user read request by applying filters,
        querying the repository, and formatting the response.

        Args:
            request (GetUserRequestDTO):
                DTO containing optional filters for user search.

            current_user (UserTable):
                Authenticated user performing the request.

        Returns:
            Dict[str, Any]:
                Result dictionary indicating success or failure,
                including sanitized user data when available.
        """

        self.logger.log_info("[workflow] processing read user")

        filters = {}

        if current_user.role != UserRole.ADMIN:
            if request.id is None:
                filters["id"] = current_user.id

        if request.id is not None:
            filters["id"] = request.id

        if request.email is not None:
            filters["email"] = request.email

        if request.name is not None:
            filters["name"] = request.name

        if request.cpf is not None:
            filters["cpf"] = request.cpf

        if request.country is not None:
            filters["country"] = request.country

        if request.role is not None:
            filters["role"] = request.role

        if request.status is not None:
            filters["status"] = request.status

        users = await self.repository.read_user(filters)

        if not users:
            self.logger.log_info("[workflow] no users found")

            return {"success": False, "message": "No users found", "data": None}

        safe_users = []

        for user in users:
            safe_users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "country": user.country,
                    "role": user.role.value,
                    "status": user.status.value,
                }
            )

        return {
            "success": True,
            "message": "Users found successfully",
            "data": safe_users,
        }

        """
        Processes the user read request by applying filters,
        querying the repository, and formatting the response.

        Args:
            db:
                Active database session used for query execution.

            request:
                DTO containing optional filters for user search.

        Returns:
            dict:
                Result dictionary indicating success or failure,
                with a message and optional user data.
        """
