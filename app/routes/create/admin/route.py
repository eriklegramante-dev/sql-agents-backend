from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.routes.create.admin.dtos.dto import (
    CreateAdminRequestDTO,
    CreateAdminResponseDTO,
)
from app.routes.create.admin.controllers.controller import CreateAdminController
from app.security.security import get_current_user
from app.models.users_table import UserTable

router = APIRouter()


@router.post(
    "/create-admin",
    summary="Create a new admin user",
    description="Creates a new admin user with validated input data. Requires admin authentication.",
    response_model=CreateAdminResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_admin(
    request: CreateAdminRequestDTO,
    current_user: UserTable = Depends(get_current_user),
) -> JSONResponse:
    """
    Endpoint to handle admin user creation requests.

    This route receives validated admin input data, delegates the creation logic
    to the controller, and returns a standardized response.

    Args:
        request (CreateAdminRequestDTO): The input data required for admin creation.

    Returns:
        CreateAdminResponseDTO: Response containing the result of the admin creation process.
    """
    controller = CreateAdminController()
    return await controller.create_admin(request, current_user)
