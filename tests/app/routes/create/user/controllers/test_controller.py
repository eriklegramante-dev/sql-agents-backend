from datetime import date

import pytest

from app.models.users_table import UserRole, UserTable
from app.routes.create.user.controllers.controller import CreateUserController
from app.routes.create.user.dtos.dto import CreateUserRequestDTO, CreateUserResponseDTO
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
        return CreateUserResponseDTO(success=True, message="created", data={"id": 1})


class ServiceFailure:
    async def handle_create(self, request):
        return CreateUserResponseDTO(success=False, message="failed", data=None)


class ServiceError:
    async def handle_create(self, request):
        raise RuntimeError("boom")


def create_request() -> CreateUserRequestDTO:
    return CreateUserRequestDTO(
        name="Standard User",
        email="standard@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


def current_user() -> UserTable:
    return UserTable(id=1, role=UserRole.ADMIN)


async def test_create_user_returns_201_for_success(fake_logger):
    controller = CreateUserController(
        service=ServiceSuccess(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_user(create_request(), current_user())

    assert response.status_code == 201
    assert response_content(response)["data"] == {"id": 1}


async def test_create_user_returns_400_for_service_failure(fake_logger):
    controller = CreateUserController(
        service=ServiceFailure(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_user(create_request(), current_user())

    assert response.status_code == 400
    assert response_content(response)["success"] is False


async def test_create_user_returns_403_for_policy_denial(fake_logger):
    controller = CreateUserController(
        service=ServiceSuccess(), policy=PolicyDeny(), logger=fake_logger
    )

    response = await controller.create_user(create_request(), current_user())

    assert response.status_code == 403
    assert (
        response_content(response)["message"]
        == "You are not authorized to create users."
    )


async def test_create_user_returns_500_for_unexpected_error(fake_logger):
    controller = CreateUserController(
        service=ServiceError(), policy=PolicyAllow(), logger=fake_logger
    )

    response = await controller.create_user(create_request(), current_user())

    assert response.status_code == 500
    assert response_content(response)["success"] is False
