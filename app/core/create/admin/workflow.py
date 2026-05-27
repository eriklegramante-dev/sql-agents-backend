from typing import Any, Dict, Optional

from app.models.users_table import UserRole
from app.security.hashing import PasswordManager
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateAdminWorkflow:
    """
    Orchestrates the creation of a new admin user in the system.

    This class manages the process of creating an admin user, including validation,
    password hashing, persistence, and logging. It leverages dependency injection
    to allow for easy testing and customization of repository, logger, and password manager.

    Attributes:
        repository (DatabaseRepository[UserTable]): Repository for database operations on UserTable.
        logger (LoggerManager): Logger manager for workflow logging.
        password_manager (PasswordManager): Manager responsible for password hashing.
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

    async def run(self, request: CreateAdminRequestDTO) -> Dict[str, Any]:
        """
        Executes the workflow to create a new admin user.

        Hashes the password, constructs the admin user model, attempts insertion
        into the database, and returns a status dictionary. Logs relevant workflow
        steps and errors throughout the process.

        Args:
            request (CreateAdminRequestDTO): The DTO containing the admin user's data.

        Returns:
            Dict[str, Any]: A dictionary with keys:
                - 'success' (bool): Indicates if the operation was successful.
                - 'message' (str): Status or error message.
                - 'data' (dict | None): Created user's ID on success, error details on failure.

        Raises:
            Exception: Propagates unexpected exceptions for logging and debugging.
        """
        self.logger.log_info("[workflow] processing create admin")
        self.logger.log_debug(f"[workflow] request dto: {request.__class__.__name__}")
        admin_user = UserTable(
            name=request.name,
            email=request.email,
            cpf=request.cpf,
            birth_date=request.birth_date,
            country=request.country,
            password=self.password_manager.hash_password(request.password),
            role=UserRole.ADMIN,
            status="ACTIVE",
        )
        self.logger.log_debug(f"[workflow] admin to insert: {admin_user}")
        admin_id = await self.repository.insert(admin_user)
        self.logger.log_debug(f"[workflow] insert result: {admin_id}")
        if not admin_id:
            self.logger.log_info("[workflow] failed to create admin")
            return {
                "success": False,
                "message": "Failed to create admin user.",
                "data": None,
            }
        self.logger.log_info("[workflow] admin user created successfully")
        return {
            "success": True,
            "message": "Admin user created successfully.",
            "data": {"id": admin_id},
        }
