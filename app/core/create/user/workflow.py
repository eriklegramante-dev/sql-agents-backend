from typing import Any, Dict, Optional

from app.models.users_table import UserRole
from app.security.hashing import PasswordManager
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateUserWorkflow:
    """
    Workflow responsible for orchestrating the user creation process.

    This class validates and processes user creation requests, handles password hashing,
    and interacts with the repository to persist new user records.

    Attributes:
        repository (DatabaseRepository[UserTable]): Repository for database operations on users.
        logger (LoggerManager): Logger for workflow events and errors.
        password_manager (PasswordManager): Manager for password hashing and verification.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[UserTable]] = None,
        logger: Optional[LoggerManager] = None,
        password_manager: Optional[PasswordManager] = None,
    ) -> None:
        self.repository = repository or DatabaseRepository(model=UserTable)
        self.logger = logger or LOGGER
        self.password_manager = password_manager or PasswordManager()

    async def run(self, request: CreateUserRequestDTO) -> Dict[str, Any]:
        """
        Processes a user creation request by validating input, hashing the password,
        and creating a new user record in the database.

        Args:
            request (CreateUserRequestDTO): DTO containing the user creation data.

        Returns:
            Dict[str, Any]: Result dictionary indicating success or failure,
                with an appropriate message and additional data.
        """
        self.logger.log_info("[workflow] processing create user")
        self.logger.log_debug(
            f"[workflow] request dto: {request.__class__.__name__}"
        )
        user = UserTable(
            name=request.name,
            email=request.email,
            cpf=request.cpf,
            birth_date=request.birth_date,
            country=request.country,
            password=self.password_manager.hash_password(request.password),
            role=UserRole.USER,
            status="ACTIVE",
        )
        self.logger.log_debug(f"[workflow] user to insert: {user}")
        user_id = await self.repository.insert(user)
        self.logger.log_debug(f"[workflow] insert result: {user_id}")
        if not user_id:
            self.logger.log_info("[workflow] failed to create user")
            return {
                "success": False,
                "message": "Failed to create user.",
                "data": None,
            }
        self.logger.log_info("[workflow] user created successfully")
        return {
            "success": True,
            "message": "User created successfully.",
            "data": {"id": user_id},
        }
