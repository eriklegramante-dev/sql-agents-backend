import pytest

from app.routes.auth.controllers.controller import LoginController
from app.routes.auth.dtos.dto import LoginResponseDTO
from tests.conftest import response_content

pytestmark = pytest.mark.asyncio


class ServiceSuccess:
    async def handle_login(self, request):
        return LoginResponseDTO(
            success=True,
            message="ok",
            access_token="token",
            token_type="bearer",
        )


class ServiceFailure:
    async def handle_login(self, request):
        return LoginResponseDTO(
            success=False,
            message="invalid",
            access_token=None,
            token_type=None,
        )


class ServiceError:
    async def handle_login(self, request):
        raise RuntimeError("boom")


async def test_login_returns_200_for_success(fake_logger):
    controller = LoginController(service=ServiceSuccess(), logger=fake_logger)

    response = await controller.login("user@example.com", "Strong@123")

    assert response.status_code == 200
    assert response_content(response)["access_token"] == "token"


async def test_login_returns_401_for_failure(fake_logger):
    controller = LoginController(service=ServiceFailure(), logger=fake_logger)

    response = await controller.login("user@example.com", "Strong@123")

    assert response.status_code == 401
    assert response_content(response)["success"] is False


async def test_login_returns_422_for_validation_error(fake_logger):
    controller = LoginController(service=ServiceSuccess(), logger=fake_logger)

    response = await controller.login("bad-email", "Strong@123")

    assert response.status_code == 422
    assert response_content(response)["success"] is False


async def test_login_returns_500_for_unexpected_error(fake_logger):
    controller = LoginController(service=ServiceError(), logger=fake_logger)

    response = await controller.login("user@example.com", "Strong@123")

    assert response.status_code == 500
    assert response_content(response)["success"] is False
