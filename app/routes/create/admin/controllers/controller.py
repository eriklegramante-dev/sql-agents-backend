from typing import Optional
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from app.routes.create.admin.dtos.dto import (
    CreateAdminRequestDTO,
    CreateAdminResponseDTO,
)
from app.routes.create.admin.services.service import CreateAdminService
from app.security.policy import UserPolicy
from app.models.users_table import UserTable
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateAdminController:
    """
    Controller responsible for handling admin user creation requests.

    This class processes incoming requests for creating new admin users,
    coordinates with the service layer, and manages logging and error handling.

    Attributes:
        logger (LoggerManager): Logger instance for recording workflow actions.
        service (CreateAdminService): Service for handling the business logic of admin creation.
    """

    def __init__(
        self,
        service: Optional[CreateAdminService] = None,
        policy: Optional[UserPolicy] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.logger = logger or LOGGER
        self.service = service or CreateAdminService()
        self.policy = policy or UserPolicy()

    async def create_admin(
        self, request: CreateAdminRequestDTO, current_user: UserTable
    ) -> JSONResponse:
        """
        Handles the HTTP request for creating a new admin user.

        Processes the request payload, invokes the service layer, and returns
        an appropriate JSON response, handling validation and unexpected errors.

        Args:
            request (CreateAdminRequestDTO): DTO containing admin creation payload.

        Returns:
            JSONResponse: A JSON response with status code, message, and data.

        Raises:
            ValidationError: If input validation fails, returns HTTP 422 with error details.
            Exception: For any other error, returns HTTP 500 with error information.
        """
        try:
            self.logger.log_info("[controller] create admin request received")
            self.logger.log_debug(
                f"[controller] request dto: {request.__class__.__name__}"
            )
            if not self.policy.can_create(request, current_user):
                self.logger.log_error("[controller] unauthorized create admin attempt")
                dto = CreateAdminResponseDTO(
                    success=False,
                    message="You are not authorized to create admin users.",
                    data=None,
                )
                return JSONResponse(status_code=403, content=dto.model_dump())

            response: CreateAdminResponseDTO = await self.service.handle_create(request)
            self.logger.log_debug(f"[controller] response: {response.model_dump()}")
            status_code = 201 if response.success else 400
            return JSONResponse(
                status_code=status_code,
                content=response.model_dump(),
            )

        except ValidationError as e:
            self.logger.log_error(f"[controller] validation error: {e.errors()}")
            dto = CreateAdminResponseDTO(
                success=False,
                message="Validation failed",
                data={"errors": e.errors()},
            )
            return JSONResponse(status_code=422, content=dto.model_dump())

        except Exception as e:
            self.logger.log_error(f"[controller] internal error: {str(e)}")
            dto = CreateAdminResponseDTO(
                success=False,
                message="Internal server error",
                data={"error": str(e)},
            )
            return JSONResponse(status_code=500, content=dto.model_dump())
