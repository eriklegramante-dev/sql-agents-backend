from typing import Dict, Any

from fastapi import APIRouter, Depends

from app.models.users_table import UserTable

from app.security.security import get_current_user

from app.routes.read.controllers.controller import (
    ReadUserController,
)

from app.routes.read.dtos.dto import (
    GetUserRequestDTO,
)

router = APIRouter(tags=["Read"])


@router.get(
    "/read",
    response_model=Dict[str, Any],
)
async def read_user(
    request: GetUserRequestDTO = Depends(),
    current_user: UserTable = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Processes authenticated user read requests.

    This endpoint receives optional user search filters,
    validates the authenticated user context,
    and returns sanitized user data according
    to the read access rules.

    Args:
        request (GetUserRequestDTO):
            DTO containing optional user search filters.

        current_user (UserTable):
            Authenticated user extracted from the access token.

    Returns:
        Dict[str, Any]:
            Dictionary containing the operation result
            and optional sanitized user data.
    """
    controller = ReadUserController()

    return await controller.handle(request=request, current_user=current_user)


@router.get(
    "/me",
    response_model=Dict[str, Any],
)
async def read_current_user(
    current_user: UserTable = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Returns sanitized data for the authenticated user.

    The user identifier comes exclusively from the validated
    bearer token through the authentication dependency.
    """
    controller = ReadUserController()

    return await controller.handle(
        request=GetUserRequestDTO(id=current_user.id),
        current_user=current_user,
    )