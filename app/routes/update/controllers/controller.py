"""HTTP controller for user profile update requests."""

from typing import Optional

from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.update.dtos.dto import (
    UpdateUserRequestDTO,
    UpdateUserResponseDTO,
)
from app.routes.update.services.service import UpdateUserService
from app.security.policy import UserPolicy


class UpdateUserController:
    """
    Controller responsible for handling user update requests.

    This class validates request-level errors, checks authorization through
    the policy layer, delegates the update execution to the service layer,
    and formats HTTP responses.

    Attributes:
        logger (LoggerManager): Logger for controller events and errors.
        service (UpdateUserService): Service instance for user update logic.
        policy (UserPolicy): Policy instance for authorization checks.
    """

    def __init__(
        self,
        service: Optional[UpdateUserService] = None,
        policy: Optional[UserPolicy] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        """Initialize update controller dependencies."""
        self.logger = logger or LOGGER
        self.service = service or UpdateUserService()
        self.policy = policy or UserPolicy()

    async def update_user(
        self,
        request: UpdateUserRequestDTO,
        current_user: UserTable,
    ) -> JSONResponse:
        """
        Update a user based on the provided request data and
        the permissions of the authenticated user.

        This method validates whether the current user has
        permission to update the target user, executes the
        update workflow, and returns a standardized JSON response.

        Args:
            request: DTO containing the user update data.
            current_user: Authenticated user performing the request.

        Returns:
            JSONResponse containing the operation result,
            including success status and message.
        """
        try:
            self.logger.log_info("[controller] update user request received")

            if not self._has_identifier(request):
                dto = UpdateUserResponseDTO(
                    success=False,
                    message="At least one identifier is required.",
                )

                return JSONResponse(
                    status_code=400,
                    content=dto.model_dump(),
                )

            if not self._has_update_fields(request):
                dto = UpdateUserResponseDTO(
                    success=False,
                    message="No update fields were provided.",
                )

                return JSONResponse(
                    status_code=400,
                    content=dto.model_dump(),
                )

            if not self.policy.can_update(request, current_user):
                dto = UpdateUserResponseDTO(
                    success=False,
                    message="You are not authorized to update this user.",
                )

                return JSONResponse(
                    status_code=403,
                    content=dto.model_dump(),
                )

            response = await self.service.handle_update(request)

            status_code = 200 if response.success else 400

            return JSONResponse(
                status_code=status_code,
                content=response.model_dump(),
            )

        except ValidationError as e:
            self.logger.log_error(f"[controller] validation error: {e.errors()}")

            dto = UpdateUserResponseDTO(
                success=False,
                message="Validation failed.",
                data={"errors": e.errors()},
            )

            return JSONResponse(
                status_code=422,
                content=dto.model_dump(),
            )

        except Exception as e:
            self.logger.log_error(f"[controller] internal error: {str(e)}")

            dto = UpdateUserResponseDTO(
                success=False,
                message="Internal server error.",
                data={"error": str(e)},
            )

            return JSONResponse(
                status_code=500,
                content=dto.model_dump(),
            )

    @staticmethod
    def _has_identifier(request: UpdateUserRequestDTO) -> bool:
        """Return whether the request identifies a user to update."""
        return any(
            [
                request.id,
                request.email,
            ]
        )

    @staticmethod
    def _has_update_fields(request: UpdateUserRequestDTO) -> bool:
        """Return whether the request contains mutable profile fields."""
        return any(
            [
                request.name,
                request.password,
            ]
        )
