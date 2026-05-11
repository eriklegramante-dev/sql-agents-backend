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
    Updates user data according to authorization rules.
    """

    controller = UpdateUserController()

    return await controller.update_user(
        request=request,
        current_user=current_user,
    )