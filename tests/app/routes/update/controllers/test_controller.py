import pytest
from pydantic import ValidationError

from app.models.users_table import UserRole, UserTable
from app.routes.update.controllers.controller import UpdateUserController
from app.routes.update.dtos.dto import (
    UpdateUserRequestDTO,
    UpdateUserResponseDTO,
)
from tests.conftest import response_content

pytestmark = pytest.mark.asyncio


class PolicyAllow:
    def can_update(self, request, current_user):
        return True


class PolicyDeny:
    def can_update(self, request, current_user):
        return False


class PolicyError:
    def can_update(self, request, current_user):
        raise RuntimeError("policy error")


class ServiceSuccess:
    async def handle_update(self, request):
        return UpdateUserResponseDTO(
            success=True,
            message="updated",
            data={"id": 1},
        )


class ServiceFailure:
    async def handle_update(self, request):
        return UpdateUserResponseDTO(
            success=False,
            message="failed",
            data=None,
        )


class ServiceError:
    async def handle_update(self, request):
        raise RuntimeError("boom")


class ServiceValidationError:
    async def handle_update(self, request):
        raise ValidationError.from_exception_data(
            "UpdateUserRequestDTO",
            [],
        )


def update_request() -> UpdateUserRequestDTO:
    return UpdateUserRequestDTO(
        id=1,
        name="Updated User",
        password="Strong@123",  # pragma: allowlist secret
    )


def current_user() -> UserTable:
    return UserTable(id=1, role=UserRole.USER)


async def test_update_user_returns_200_for_success(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceSuccess(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 200

    assert response_content(response)["data"] == {"id": 1}


async def test_update_user_returns_400_for_service_failure(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceFailure(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 400

    assert response_content(response)["success"] is False


async def test_update_user_returns_403_for_policy_denial(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceSuccess(),
        policy=PolicyDeny(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 403

    assert (
        response_content(response)["message"]
        == "You are not authorized to update this user."
    )


async def test_update_user_returns_500_for_unexpected_error(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceError(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 500

    assert response_content(response)["success"] is False


async def test_update_user_returns_500_when_policy_raises_error(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceSuccess(),
        policy=PolicyError(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 500

    assert response_content(response)["success"] is False


async def test_update_user_returns_400_for_validation_error(
    fake_logger,
):
    controller = UpdateUserController(
        service=ServiceValidationError(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    response = await controller.update_user(
        update_request(),
        current_user(),
    )

    assert response.status_code == 422

    assert response_content(response)["success"] is False
