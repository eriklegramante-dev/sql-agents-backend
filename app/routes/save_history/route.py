from fastapi import APIRouter, Depends

from app.models.users_table import UserTable
from app.security.security import get_current_user

from app.routes.save_history.controllers.controller import (
    SaveHistoryController,
)

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
)

router = APIRouter(tags=["Save History"])


@router.post("/save-history")
async def save_history(
    request: SaveHistoryRequestDTO,
    current_user: UserTable = Depends(get_current_user),
):
    controller = SaveHistoryController()

    return await controller.handle(
        request=request,
        current_user=current_user,
    )
