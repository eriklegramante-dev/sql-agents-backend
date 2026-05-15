from fastapi import APIRouter, Depends

from app.security.security import get_current_user
from app.models.users_table import UserTable

from app.routes.update.controllers.controller import (
    UpdateUserController,
)

from app.routes.update.dtos.dto import (
    UpdateUserRequestDTO,
)


router = APIRouter(
    tags=["Update"],
)


@router.put("/update")
async def update_user(
    request: UpdateUserRequestDTO,
    current_user: UserTable = Depends(get_current_user),
):
    """
    Updates user profile information through the authenticated update workflow.

    Receives the validated update payload and the authenticated user context,
    delegates authorization and update execution to the controller and service
    layers, and returns a standardized HTTP response containing the operation result.

    Args:
        request (UpdateUserRequestDTO):
            DTO containing validated user update data.
        current_user (UserTable):
            Authenticated user extracted from the access token.

    Returns:
        JSONResponse:
            HTTP response containing the update operation result.
    """

    controller = UpdateUserController()

    return await controller.update_user(
        request=request,
        current_user=current_user,
    )
