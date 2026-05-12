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
    Endpoint responsible for deleting users.

    Responsibilities:
    - Receive validated delete DTO
    - Inject authenticated user
    - Delegate processing to controller

    Authorization rules are handled by UserPolicy.
    """

    controller = DeleteUserController()

    return await controller.delete_user(
        request=user_data,
        current_user=current_user,
    )