from fastapi import APIRouter, Depends

from app.models.users_table import UserTable
from app.security.security import get_current_user

from app.routes.save_history.controllers.controller import (
    SaveHistoryController,
)

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
)

router = APIRouter(tags=["Save History"])


@router.post("/save-history")
async def save_history(
    request: SaveHistoryRequestDTO,
    current_user: UserTable = Depends(get_current_user),
):
    """
    Creates history or atomically saves a session for the authenticated user.

    Receives the history data, validates the authenticated user
    context, and delegates the request processing through the
    controller, service, and workflow layers.

    Args:
        request (SaveHistoryRequestDTO):
            History data to be persisted.

        current_user (UserTable):
            Authenticated user obtained from the
            security dependency.

    Returns:
        JSONResponse:
            Standardized response containing the
            operation result and saved history identifier.
    """

    controller = SaveHistoryController()

    return await controller.handle(
        request=request,
        current_user=current_user,
    )
