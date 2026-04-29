from datetime import date

import pytest

from app.models.users_table import UserRole, UserTable
from app.routes.create.admin.controllers.controller import CreateAdminController
from app.routes.create.admin.dtos.dto import (
    CreateAdminRequestDTO,
    CreateAdminResponseDTO,
)
from tests.conftest import response_content

pytestmark = pytest.mark.asyncio


class PolicyAllow:
    def can_create(self, request, current_user):
        return True


class PolicyDeny:
    def can_create(self, request, current_user):
        return False


class ServiceSuccess:
    async def handle_create(self, request):
        return CreateAdminResponseDTO(success=True, message="created", data={"id": 1})


class ServiceFailure:
    async def handle_create(self, request):
        return CreateAdminResponseDTO(success=False, message="failed", data=None)


class ServiceError:
    async def handle_create(self, request):
        raise RuntimeError("boom")


def create_request() -> CreateAdminRequestDTO:
    return CreateAdminRequestDTO(
        name="Admin User",
        email="admin@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


def current_user() -> UserTable:
    return UserTable(id=1, role=UserRole.ADMIN)


async def test_create_admin_returns_201_for_success(fake_logger):
    controller = CreateAdminController(
        service=ServiceSuccess(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_admin(create_request(), current_user())

    assert response.status_code == 201
    assert response_content(response)["data"] == {"id": 1}


async def test_create_admin_returns_400_for_service_failure(fake_logger):
    controller = CreateAdminController(
        service=ServiceFailure(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_admin(create_request(), current_user())

    assert response.status_code == 400
    assert response_content(response)["success"] is False


async def test_create_admin_returns_403_for_policy_denial(fake_logger):
    controller = CreateAdminController(
        service=ServiceSuccess(), policy=PolicyDeny(), logger=fake_logger
    )

    response = await controller.create_admin(create_request(), current_user())

    assert response.status_code == 403
    assert response_content(response)["message"] == "You are not authorized to create admin users."


async def test_create_admin_returns_500_for_unexpected_error(fake_logger):
    controller = CreateAdminController(
        service=ServiceError(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_admin(create_request(), current_user())

    assert response.status_code == 500
    assert response_content(response)["success"] is False
