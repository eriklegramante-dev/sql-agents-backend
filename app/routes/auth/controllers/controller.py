from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.routes.auth.dtos.dto import LoginRequestDTO, LoginResponseDTO
from app.routes.auth.services.service import LoginService
from app.logs.setup_logger import LoggerManager, LOGGER


class LoginController:
    """
    Controller responsible for handling user authentication requests.

    This class coordinates the receipt and processing of login requests,
    delegates authentication logic to the service layer, and manages response formatting.

    Attributes:
        service (LoginService): Service instance responsible for authentication logic.
        logger (LoggerManager): Logger instance for logging events and errors.
    """

    def __init__(
        self,
        service: Optional[LoginService] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.service = service or LoginService()
        self.logger = logger or LOGGER

    async def login(self, username: str, password: str) -> JSONResponse:
        """
        Processes a login request, performing validation and authentication.

        Receives username and password, constructs the login request DTO, and delegates
        the authentication logic to the service layer. Handles all error scenarios and logs
        key steps during processing.

        Args:
            username (str): User email address used for authentication.
            password (str): User password.

        Returns:
            JSONResponse: JSON response containing the result of the authentication attempt,
                including an access token if authentication is successful.

        Raises:
            ValidationError: If input validation fails, returns a 422 response with details.
            Exception: If any unexpected error occurs, returns a 500 response with an error message.
        """
        try:
            self.logger.log_info("[controller] Login request received")
            request = LoginRequestDTO(username=username, password=password)
            self.logger.log_debug(f"[controller] Login username: {request.username}")

            response: LoginResponseDTO = await self.service.handle_login(request)
            self.logger.log_debug(f"[controller] login success: {response.success}")
            if response.success:
                self.logger.log_info(
                    f"[controller] User '{request.username}' logged in successfully"
                )
                status_code = 200
            else:
                self.logger.log_info(
                    f"[controller] Authentication failed for user '{request.username}'"
                )
                status_code = 401
            return JSONResponse(status_code=status_code, content=response.model_dump())

        except ValidationError as e:
            self.logger.log_error(f"[controller] Validation error during login: {e}")
            dto = LoginResponseDTO(
                access_token="",
                token_type="bearer",
                success=False,
                message=f"Validation error - {e}",
            )
            return JSONResponse(status_code=422, content=dto.model_dump())

        except Exception as e:
            self.logger.log_error(f"[controller] Unexpected error during login: {e}")
            dto = LoginResponseDTO(
                access_token="",
                token_type="bearer",
                success=False,
                message=f"Internal server error - {e}",
            )
            return JSONResponse(status_code=500, content=dto.model_dump())
