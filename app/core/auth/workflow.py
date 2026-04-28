from typing import Dict, Any, Optional

from app.routes.auth.dtos.dto import LoginRequestDTO
from app.security.hashing import PasswordManager
from app.models.users_table import UserTable
from app.database.repository import DatabaseRepository
from app.security.authenticator import JWTAuthenticator
from app.logs.setup_logger import LoggerManager, LOGGER


class LoginWorkflow:
    """
    Workflow responsible for handling the user authentication process.

    This class validates user credentials, verifies passwords, and generates
    JWT access tokens for authenticated users.

    Attributes:
        repository (DatabaseRepository[UserTable]): Repository for user database operations.
        logger (LoggerManager): Logger for workflow events and errors.
        authenticator (JWTAuthenticator): Authenticator for creating JWT access tokens.
        password_manager (PasswordManager): Manager for password hashing and verification.
    """

    def __init__(
        self,
        repository: Optional[DatabaseRepository[UserTable]] = None,
        logger: Optional[LoggerManager] = None,
        authenticator: Optional[JWTAuthenticator] = None,
        password_manager: Optional[PasswordManager] = None,
    ) -> None:
        self.repository = repository or DatabaseRepository(model=UserTable)
        self.logger = logger or LOGGER
        self.authenticator = authenticator or JWTAuthenticator()
        self.password_manager = password_manager or PasswordManager()

    async def run(self, request: LoginRequestDTO) -> Dict[str, Any]:
        """
        Processes a login request by verifying user credentials and generating a JWT token.

        Args:
            request (LoginRequestDTO): DTO containing the login credentials.

        Returns:
            Dict[str, Any]: Result dictionary indicating authentication success or failure,
                including a JWT access token if successful.
        """
        self.logger.log_info("[workflow] processing login")
        self.logger.log_debug(f"[workflow] login username: {request.username}")
        user = await self.repository.get_user_by_email(request.username)
        self.logger.log_debug(f"[workflow] user lookup result: {user}")
        if not user or not self.password_manager.verify_password(
            request.password, user.password
        ):
            self.logger.log_info("[workflow] invalid credentials")
            return {
                "success": False,
                "message": "Invalid credentials.",
                "access_token": None,
                "token_type": None,
            }
        token = self.authenticator.create_access_token(str(user.id))
        updated = await self.repository.update_last_login_at(user.id)
        if not updated:
            self.logger.log_debug(
                f"[workflow] failed to update last_login_at for user {user.id}"
            )

        self.logger.log_info("[workflow] login successful")
        return {
            "success": True,
            "message": "Login successful.",
            "access_token": token,
            "token_type": "bearer",
        }
