from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.models.users_table import UserTable
from app.routes.chat_sessions.controllers.controller import (
    ChatSessionCountController,
)
from app.routes.chat_sessions.dependencies.dependencie import (
    get_chat_session_count_controller,
)
from app.routes.chat_sessions.dtos.dto import ChatSessionCountResponseDTO
from app.security.security import get_current_user


router = APIRouter(tags=["Chat Sessions"])


@router.get(
    "/chat/sessions/count",
    response_model=ChatSessionCountResponseDTO,
)
async def count_chat_sessions(
    current_user: UserTable = Depends(get_current_user),
    controller: ChatSessionCountController = Depends(
        get_chat_session_count_controller,
    ),
) -> JSONResponse:
    """Count saved conversation sessions for the authenticated user.

    Includes active and archived histories with a session identifier.
    Excludes deleted histories and legacy entries without a session.
    The user identity comes exclusively from the authenticated token.
    controller: Controller supplied by the composition dependency.

    Args:
        current_user: User resolved by the authentication dependency.

    Returns:
        Response containing the total or an explicit operation failure.
    """

    return await controller.execute(user_id=current_user.id)