from typing import Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.routes.read.services.services import ReadUserService
from app.routes.read.dtos.dto import GetUserRequestDTO
from app.security.policy import UserPolicy
from app.logs.setup_logger import LoggerManager, LOGGER


class ReadUserController:
    """
    Controller responsible for handling user read requests.

    This class validates authorization rules,
    delegates authorized requests to the service layer,
    and returns standardized JSON responses.

    Attributes:
        service (ReadUserService):
            Service responsible for user read operations.

        logger (LoggerManager):
            Logger instance for controller logs.

        policy (UserPolicy):
            Policy responsible for RBAC authorization validation.
    """

    def __init__(
        self,
        service: Optional[ReadUserService] = None,
        logger: Optional[LoggerManager] = None,
        policy: Optional[UserPolicy] = None,
    ) -> None:

        self.service = service or ReadUserService()

        self.logger = logger or LOGGER

        self.policy = policy or UserPolicy()

    async def handle(
        self,
        request: GetUserRequestDTO,
        current_user,
    ) -> JSONResponse:
        """
        Handles the user read request.

        Validates user authorization through RBAC policy,
        delegates authorized requests to the service layer,
        and returns standardized JSON responses.

        Args:
            request (GetUserRequestDTO):
                DTO containing user read filters.

            current_user:
                Authenticated user performing the request.

        Returns:
            JSONResponse:
                Standardized API response.
        """
        
        try:
            self.logger.log_info(
                "[controller] Read user request received"
            )

            authorized = self.policy.can_view(
                request=request,
                current_user=current_user,
            )

            if not authorized:

                self.logger.log_info(
                    f"[controller] Access denied for user "
                    f"{current_user.id}"
                )

                raise HTTPException(
                    status_code=403,
                    detail="Not authorized"
                )

            self.logger.log_debug(
                f"[controller] User {current_user.id} authorized"
            )

            response = await self.service.handle_read(
                request=request,
                current_user=current_user
            )

            self.logger.log_info(
                "[controller] Read user request completed"
            )

            return JSONResponse(
                status_code=200,
                content=response.model_dump()
            )
        
        except ValidationError as e:
            self.logger.log_error(
                f"[controller] Validation error occurred: {e}"
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid request data"
            )
        
        except HTTPException as e:
            raise

        except Exception as e:
            self.logger.log_error(
                f"[controller] An error occurred: {e}"
            )
            raise HTTPException(
                status_code=500,
                detail="Internal server error"
            )