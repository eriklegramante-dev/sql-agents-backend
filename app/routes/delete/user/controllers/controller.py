from typing import Optional

from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.logs.setup_logger import LOGGER, LoggerManager
from app.models.users_table import UserTable
from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)
from app.routes.delete.user.services.service import DeleteUserService
from app.security.policy import UserPolicy


class DeleteUserController:
    """
    Controller responsible for handling user deletion requests.
    """

    def __init__(
        self,
        service: Optional[DeleteUserService] = None,
        policy: Optional[UserPolicy] = None,
        logger: Optional[LoggerManager] = None,
    ) -> None:

        self.service = service or DeleteUserService()
        self.policy = policy or UserPolicy()
        self.logger = logger or LOGGER

    async def delete_user(
        self,
        request: DeleteUserRequestDTO,
        current_user: UserTable,
    ) -> JSONResponse:

        try:

            self.logger.log_info(
                "[controller] delete user request received"
            )

            self._validate_delete_request(request)

            self._authorize_delete(
                request=request,
                current_user=current_user,
            )

            response = await self.service.handle_delete(request)

            status_code = 200 if response.success else 400

            return JSONResponse(
                status_code=status_code,
                content=response.model_dump(),
            )

        except PermissionError as e:

            self.logger.log_error(str(e))

            dto = DeleteUserResponseDTO(
                success=False,
                message=str(e),
                data=None,
            )

            return JSONResponse(
                status_code=403,
                content=dto.model_dump(),
            )

        except ValidationError as e:

            self.logger.log_error(
                f"[controller] validation error: {e.errors()}"
            )

            dto = DeleteUserResponseDTO(
                success=False,
                message="Validation failed",
                data=None,
            )

            return JSONResponse(
                status_code=422,
                content=dto.model_dump(),
            )

        except ValueError as e:

            self.logger.log_error(str(e))

            dto = DeleteUserResponseDTO(
                success=False,
                message=str(e),
                data=None,
            )

            return JSONResponse(
                status_code=400,
                content=dto.model_dump(),
            )

        except Exception as e:

            self.logger.log_error(
                f"[controller] internal error: {str(e)}"
            )

            dto = DeleteUserResponseDTO(
                success=False,
                message="Internal server error",
                data=None,
            )

            return JSONResponse(
                status_code=500,
                content=dto.model_dump(),
            )

    def _validate_delete_request(
        self,
        request: DeleteUserRequestDTO,
    ) -> None:

        if not request.id and not request.email and not request.cpf:

            raise ValueError(
                "You must provide id, email or cpf."
            )

    def _authorize_delete(
        self,
        request: DeleteUserRequestDTO,
        current_user: UserTable,
    ) -> None:

        authorized = self.policy.can_delete(
            request=request,
            current_user=current_user,
        )

        if not authorized:

            raise PermissionError(
                "You are not authorized to delete this user."
            )