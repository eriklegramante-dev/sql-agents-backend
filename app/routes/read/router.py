from fastapi import APIRouter, Depends

from app.models.users_table import UserTable 

from app.security.security import get_current_user

from app.routes.read.controllers.controller import (
    ReadUserController,
)

from app.routes.read.dtos.dto import (
    GetUserRequestDTO,
)

router = APIRouter(
    tags=["Read"]
)


@router.get("/read")                
async def read_user(                              
    request: GetUserRequestDTO = Depends(),            
    current_user: UserTable = Depends(get_current_user)
):
    """
    Route responsible for processing user read requests.

    This endpoint receives search filters,
    validates the authenticated user,
    and returns user data based on the request.

    Args:
        request (GetUserRequestDTO):
            DTO containing user search filters.

        db (Session):
            Active database session.

        current_user:
            Authenticated user performing the request.

    Returns:
        dict:
            Response containing the operation result
            and optional user data.
    """    
    controller = ReadUserController()
    
    return await controller.handle(
        request=request,
        current_user=current_user
   )

