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
    Handles user update requests and authorization flow.
    """

    def __init__(
        self,
        service: Optional[UpdateUserService] = None,
        policy: Optional[UserPolicy] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:
        self.logger = logger or LOGGER
        self.service = service or UpdateUserService()
        self.policy = policy or UserPolicy()

    async def update_user(
        self,
        request: UpdateUserRequestDTO,
        current_user: UserTable,
    ) -> JSONResponse:
        """
        Validates requests, checks authorization
        and delegates execution to the service layer.
        """
        try:
            self.logger.log_info(
                "[controller] update user request received"
            )

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
            self.logger.log_error(
                f"[controller] validation error: {e.errors()}"
            )

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
            self.logger.log_error(
                f"[controller] internal error: {str(e)}"
            )

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
        return any([
            request.id,
            request.email,
        ])

    @staticmethod
    def _has_update_fields(request: UpdateUserRequestDTO) -> bool:
        return any([
            request.name,
            request.password,
        ])