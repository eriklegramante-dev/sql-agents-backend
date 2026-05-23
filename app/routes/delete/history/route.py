from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.models.users_table import UserTable
from app.routes.delete.history.controllers.controller import (
    DeleteHistoryController,
)
from app.routes.delete.history.dtos.dto import (
    DeleteHistoryResponseDTO,
)
from app.security.security import get_current_user

router = APIRouter()


@router.delete(
    "/delete-history",
    summary="Delete oldest chat history",
    description=("Deletes the oldest chat history record for the authenticated user."),
    response_model=DeleteHistoryResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def delete_history(
    current_user: UserTable = Depends(get_current_user),
) -> JSONResponse:
    """
    Deletes the oldest chat history record for the authenticated user.

    Receives the authenticated user context and delegates the
    delete operation to the controller layer.

    Args:
        current_user (UserTable): Authenticated user performing the
            delete operation.

    Returns:
        JSONResponse: Standardized HTTP response containing the
            delete history operation result.
    """

    controller = DeleteHistoryController()

    return await controller.delete_history(
        current_user=current_user,
    )
