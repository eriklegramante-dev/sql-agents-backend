from fastapi import APIRouter, Depends

from app.models.users_table import UserTable
from app.security.security import get_current_user

from app.routes.recent_history.controllers.controller import (
    RecentHistoryController,
)


router = APIRouter(
    tags=["Recent History"],
)


@router.get("/recent-history")
async def get_recent_history(
    current_user: UserTable = Depends(get_current_user),
):
    """
    Retrieve the most recent history entries
    for the authenticated user.

    Receives the authenticated user context,
    delegates the recent history retrieval
    process to the controller and service
    layers, and returns a standardized HTTP
    response containing the user's recent
    conversation history.

    Args:
        current_user (UserTable):
            Authenticated user extracted
            from the access token.

    Returns:
        JSONResponse:
            HTTP response containing the
            recent history retrieval result.
    """

    controller = RecentHistoryController()

    return await controller.get_recent_history(
        current_user=current_user,
    )
