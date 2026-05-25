import pytest
from fastapi.responses import JSONResponse

from app.models.users_table import UserRole, UserTable
from app.routes.delete.history.route import delete_history


class FakeDeleteHistoryController:
    called_with_current_user = None

    async def delete_history(self, current_user):
        FakeDeleteHistoryController.called_with_current_user = current_user

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Chat history deleted successfully.",
                "data": {
                    "deleted_history_id": 1,
                },
            },
        )


@pytest.mark.asyncio
async def test_delete_history_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(
        "app.routes.delete.history.route.DeleteHistoryController",
        FakeDeleteHistoryController,
    )

    current_user = UserTable(
        id=1,
        role=UserRole.USER,
        email="user@example.com",
        cpf="12345678901",
    )

    response = await delete_history(
        current_user=current_user,
    )

    assert response.status_code == 200
    assert FakeDeleteHistoryController.called_with_current_user is current_user


class FakeDeleteHistoryControllerFailure:
    async def delete_history(self, current_user):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Chat history not found.",
                "data": None,
            },
        )


@pytest.mark.asyncio
async def test_delete_history_route_returns_controller_failure(monkeypatch):
    monkeypatch.setattr(
        "app.routes.delete.history.route.DeleteHistoryController",
        FakeDeleteHistoryControllerFailure,
    )

    current_user = UserTable(
        id=1,
        role=UserRole.USER,
        email="user@example.com",
        cpf="12345678901",
    )

    response = await delete_history(
        current_user=current_user,
    )

    assert response.status_code == 404
