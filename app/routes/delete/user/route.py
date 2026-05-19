from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)

from app.routes.delete.user.controllers.controller import (
    DeleteUserController,
)

from app.security.security import get_current_user

from app.models.users_table import UserTable


router = APIRouter()


@router.delete(
    "/delete",
    summary="Delete a user",
    description=(
        "Deletes a user account based on id, email, or cpf. "
        "Authorization is enforced through RBAC policy."
    ),
    response_model=DeleteUserResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_data: DeleteUserRequestDTO,
    current_user: UserTable = Depends(get_current_user),
) -> JSONResponse:
    """
    Deletes a user account for the authenticated user.

    Receives the delete request payload, validates the authenticated
    user context, and delegates the delete operation to the controller layer.

    Args:
        user_data (DeleteUserRequestDTO): DTO containing the user
            identifier used for deletion.
        current_user (UserTable): Authenticated user performing
            the delete operation.

    Returns:
        JSONResponse: Standardized HTTP response containing the
            delete operation result.
    """

    controller = DeleteUserController()

    return await controller.delete_user(
        request=user_data,
        current_user=current_user,
    )