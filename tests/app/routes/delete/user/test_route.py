import pytest
from fastapi.responses import JSONResponse

from app.models.users_table import UserRole, UserTable
from app.routes.delete.user.dtos.dto import DeleteUserRequestDTO
from app.routes.delete.user.route import delete_user


class FakeDeleteUserController:
    called_with_request = None
    called_with_current_user = None

    async def delete_user(self, request, current_user):
        FakeDeleteUserController.called_with_request = request
        FakeDeleteUserController.called_with_current_user = current_user

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User deleted successfully.",
                "deleted_user_id": request.id,
            },
        )


@pytest.mark.asyncio
async def test_delete_user_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(
        "app.routes.delete.user.route.DeleteUserController",
        FakeDeleteUserController,
    )

    request = DeleteUserRequestDTO(id=1)

    current_user = UserTable(
        id=1,
        role=UserRole.USER,
        email="user@example.com",
        cpf="12345678901",
    )

    response = await delete_user(
        user_data=request,
        current_user=current_user,
    )

    assert response.status_code == 200
    assert FakeDeleteUserController.called_with_request is request
    assert FakeDeleteUserController.called_with_current_user is current_user


class FakeDeleteUserControllerFailure:
    async def delete_user(self, request, current_user):
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "message": "Not authorized.",
                "deleted_user_id": None,
            },
        )


@pytest.mark.asyncio
async def test_delete_user_route_returns_controller_failure(monkeypatch):
    monkeypatch.setattr(
        "app.routes.delete.user.route.DeleteUserController",
        FakeDeleteUserControllerFailure,
    )

    request = DeleteUserRequestDTO(id=2)

    current_user = UserTable(
        id=1,
        role=UserRole.USER,
        email="user@example.com",
        cpf="12345678901",
    )

    response = await delete_user(
        user_data=request,
        current_user=current_user,
    )

    assert response.status_code == 403
