from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.routes.create.user.dtos.dto import CreateUserRequestDTO, CreateUserResponseDTO
from app.routes.create.user.controllers.controller import CreateUserController
from app.security.security import get_current_user
from app.models.users_table import UserTable


router = APIRouter()


@router.post(
    "/create",
    summary="Create a new user",
    description="Creates a new user with validated input data. Requires admin authentication.",
    response_model=CreateUserResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: CreateUserRequestDTO,
    current_user: UserTable = Depends(get_current_user),
) -> JSONResponse:
    """
    Endpoint to handle user creation requests.

    This route receives validated user input data, delegates the user creation logic
    to the controller, and returns a standardized response.

    Args:
        user_data (CreateUserRequestDTO): The input data required for user creation.

    Returns:
        CreateUserResponseDTO: Response containing the result of the user creation process.
    """
    controller = CreateUserController()
    return await controller.create_user(user_data, current_user)
