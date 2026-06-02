from typing import Optional
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from app.routes.create.user.dtos.dto import CreateUserRequestDTO, CreateUserResponseDTO
from app.routes.create.user.services.service import CreateUserService
from app.security.policy import UserPolicy
from app.models.users_table import UserTable
from app.logs.setup_logger import LoggerManager, LOGGER


class CreateUserController:
    """
    Controller responsible for handling user creation requests.

    This class coordinates the receipt, validation, and processing of user creation requests,
    delegates business logic to the service layer, and handles response formatting and error logging.

    Attributes:
        logger (LoggerManager): Logger for controller events and errors.
        service (CreateUserService): Service instance for business logic related to user creation.
    """

    def __init__(
        self,
        service: Optional[CreateUserService] = None,
        policy: Optional[UserPolicy] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.logger = logger or LOGGER
        self.service = service or CreateUserService()
        self.policy = policy or UserPolicy()

    async def create_user(
        self, request: CreateUserRequestDTO, current_user: UserTable
    ) -> JSONResponse:
        """
        Processes a user creation request, invoking the service layer and handling errors.

        Args:
            request (CreateUserRequestDTO): The DTO containing user creation data.

        Returns:
            JSONResponse: A FastAPI JSONResponse with status code and message describing the outcome.

        Raises:
            ValidationError: If request data fails validation, returns 422 response.
            Exception: For any unexpected errors, returns 500 response.
        """
        try:
            self.logger.log_info("[controller] create user request received")
            self.logger.log_debug(
                f"[controller] request dto: {request.__class__.__name__}"
            )
            if not self.policy.can_create(request, current_user):
                self.logger.log_error("[controller] unauthorized create user attempt")
                dto = CreateUserResponseDTO(
                    success=False,
                    message="You are not authorized to create users.",
                    data=None,
                )
                return JSONResponse(status_code=403, content=dto.model_dump())

            response: CreateUserResponseDTO = await self.service.handle_create(request)
            self.logger.log_debug(f"[controller] response: {response.model_dump()}")
            status_code = 201 if response.success else 422
            return JSONResponse(
                status_code=status_code,
                content=response.model_dump(),
            )

        except ValidationError as e:
            self.logger.log_error(f"[controller] validation error: {e.errors()}")
            dto = CreateUserResponseDTO(
                success=False,
                message="Validation failed",
                data={"errors": e.errors()},
            )
            return JSONResponse(status_code=422, content=dto.model_dump())

        except Exception as e:
            self.logger.log_error(f"[controller] internal error: {str(e)}")
            dto = CreateUserResponseDTO(
                success=False,
                message="Internal server error",
                data={"error": str(e)},
            )
            return JSONResponse(status_code=500, content=dto.model_dump())
