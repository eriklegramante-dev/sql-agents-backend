from fastapi import APIRouter, status, Form
from fastapi.responses import JSONResponse

from app.routes.auth.dtos.dto import LoginResponseDTO
from app.routes.auth.controllers.controller import LoginController

router = APIRouter()


@router.post(
    "/token",
    summary="get JWT token",
    description="Authenticates the user and returns a JWT access token for use in protected endpoints.",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def login(
    username: str = Form(
        ...,
        description="User email address. Example: user@example.com",
        min_length=5,
        max_length=128,
    ),
    password: str = Form(
        ...,
        min_length=8,
        max_length=128,
        description="User password. Example: MyStr0ngP@ssw0rd!",
    ),
) -> JSONResponse:
    """
    Authenticates the user and returns a JWT access token.

    This endpoint receives the user's credentials, performs authentication, and, if successful,
    returns a JWT access token for use in protected endpoints.

    Args:
        username (str): User email address. Must be between 5 and 128 characters.
        password (str): User password. Must be between 8 and 128 characters.

    Returns:
        LoginResponseDTO: Object containing the JWT access token and additional user information.

    Raises:
        HTTPException: If authentication fails, an HTTPException with status 401 is returned.
    """
    controller = LoginController()
    return await controller.login(username, password)
