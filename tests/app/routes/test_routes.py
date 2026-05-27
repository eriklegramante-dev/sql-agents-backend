from datetime import date

import pytest

from app.models.users_table import UserRole, UserTable
from app.routes.auth import route as auth_route
from app.routes.create.admin import route as create_admin_route
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user import route as create_user_route
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.routes.recent_history import route as recent_history_route
from app.routes.update import route as update_route
from app.routes.update.dtos.dto import UpdateUserRequestDTO

pytestmark = pytest.mark.asyncio


class LoginController:
    async def login(self, username, password):
        return {"username": username, "password": password}


class CreateUserController:
    async def create_user(self, user_data, current_user):
        return {"email": user_data.email, "current_user": current_user.id}


class CreateAdminController:
    async def create_admin(self, request, current_user):
        return {"email": request.email, "current_user": current_user.id}


class UpdateUserController:
    async def update_user(self, request, current_user):
        return {"id": request.id, "name": request.name, "current_user": current_user.id}


class RecentHistoryController:
    async def get_recent_history(self, current_user):
        return {"current_user": current_user.id}


@pytest.mark.asyncio
async def test_login_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(auth_route, "LoginController", LoginController)

    result = await auth_route.login("user@example.com", "Strong@123")

    assert result == {"username": "user@example.com", "password": "Strong@123"}


@pytest.mark.asyncio
async def test_create_user_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(create_user_route, "CreateUserController", CreateUserController)
    request = CreateUserRequestDTO(
        name="Standard User",
        email="standard@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )
    current_user = UserTable(id=1, role=UserRole.ADMIN)

    result = await create_user_route.create_user(request, current_user)

    assert result == {"email": "standard@example.com", "current_user": 1}


@pytest.mark.asyncio
async def test_create_admin_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(
        create_admin_route, "CreateAdminController", CreateAdminController
    )
    request = CreateAdminRequestDTO(
        name="Admin User",
        email="admin@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )
    current_user = UserTable(id=1, role=UserRole.ADMIN)

    result = await create_admin_route.create_admin(request, current_user)

    assert result == {"email": "admin@example.com", "current_user": 1}


@pytest.mark.asyncio
async def test_update_user_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(update_route, "UpdateUserController", UpdateUserController)
    request = UpdateUserRequestDTO(
        id=1,
        name="Updated User",
        password="Strong@123",
    )
    current_user = UserTable(id=1, role=UserRole.USER)

    result = await update_route.update_user(request, current_user)

    assert result == {"id": 1, "name": "Updated User", "current_user": 1}


@pytest.mark.asyncio
async def test_recent_history_route_delegates_to_controller(monkeypatch):
    monkeypatch.setattr(
        recent_history_route,
        "RecentHistoryController",
        RecentHistoryController,
    )
    current_user = UserTable(id=1, role=UserRole.USER)

    result = await recent_history_route.get_recent_history(current_user)

    assert result == {"current_user": 1}
