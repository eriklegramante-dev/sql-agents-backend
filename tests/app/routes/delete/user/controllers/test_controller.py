import pytest
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.routes.delete.user.controllers.controller import DeleteUserController
from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)


class CurrentUser:
    def __init__(self, user_id=1):
        self.id = user_id


class Service:
    def __init__(self, response=None, raises=False):
        self.response = response
        self.raises = raises
        self.request = None

    async def handle_delete(self, request):
        if self.raises:
            raise RuntimeError("boom")

        self.request = request
        return self.response


class Policy:
    def __init__(self, authorized=True):
        self.authorized = authorized
        self.request = None
        self.current_user = None

    def can_delete(self, request, current_user):
        self.request = request
        self.current_user = current_user
        return self.authorized


def create_request(
    user_id=8,
    email=None,
    cpf=None,
) -> DeleteUserRequestDTO:
    return DeleteUserRequestDTO(
        id=user_id,
        email=email,
        cpf=cpf,
    )


@pytest.mark.asyncio
async def test_delete_user_returns_success_response(fake_logger):
    service_response = DeleteUserResponseDTO(
        success=True,
        message="User deleted successfully.",
        deleted_user_id=8,
    )

    service = Service(response=service_response)
    policy = Policy(authorized=True)

    controller = DeleteUserController(
        service=service,
        policy=policy,
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(user_id=8),
        current_user=CurrentUser(user_id=8),
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert service.request.id == 8
    assert policy.request.id == 8
    assert policy.current_user.id == 8


@pytest.mark.asyncio
async def test_delete_user_returns_bad_request_when_service_fails(fake_logger):
    service_response = DeleteUserResponseDTO(
        success=False,
        message="User not found or could not be deleted.",
        deleted_user_id=None,
    )

    controller = DeleteUserController(
        service=Service(response=service_response),
        policy=Policy(authorized=True),
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(user_id=99),
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_returns_forbidden_when_not_authorized(fake_logger):
    controller = DeleteUserController(
        service=Service(),
        policy=Policy(authorized=False),
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(user_id=2),
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_returns_bad_request_when_no_filter_is_provided(fake_logger):
    controller = DeleteUserController(
        service=Service(),
        policy=Policy(authorized=True),
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(
            user_id=None,
            email=None,
            cpf=None,
        ),
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user_returns_internal_server_error(fake_logger):
    controller = DeleteUserController(
        service=Service(raises=True),
        policy=Policy(authorized=True),
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(user_id=8),
        current_user=CurrentUser(user_id=8),
    )

    assert response.status_code == 500


def test_validate_delete_request_raises_value_error(fake_logger):
    controller = DeleteUserController(
        service=Service(),
        logger=fake_logger,
    )

    with pytest.raises(ValueError, match="You must provide id, email or cpf."):
        controller._validate_delete_request(
            create_request(
                user_id=None,
                email=None,
                cpf=None,
            )
        )


def test_authorize_delete_raises_permission_error(fake_logger):
    controller = DeleteUserController(
        service=Service(),
        policy=Policy(authorized=False),
        logger=fake_logger,
    )

    with pytest.raises(
        PermissionError,
        match="You are not authorized to delete this user.",
    ):
        controller._authorize_delete(
            request=create_request(user_id=2),
            current_user=CurrentUser(user_id=1),
        )


def test_authorize_delete_does_not_raise_when_authorized(fake_logger):
    controller = DeleteUserController(
        service=Service(),
        policy=Policy(authorized=True),
        logger=fake_logger,
    )

    controller._authorize_delete(
        request=create_request(user_id=1),
        current_user=CurrentUser(user_id=1),
    )


class ServiceWithValidationError:
    async def handle_delete(self, request):
        raise ValidationError.from_exception_data(
            "DeleteUserRequestDTO",
            [
                {
                    "type": "value_error",
                    "loc": ("cpf",),
                    "msg": "CPF must contain only digits.",
                    "input": "invalid-cpf",
                    "ctx": {
                        "error": ValueError("CPF must contain only digits.")
                    },
                }
            ],
        )


@pytest.mark.asyncio
async def test_delete_user_returns_validation_error(fake_logger):
    controller = DeleteUserController(
        service=ServiceWithValidationError(),
        policy=Policy(authorized=True),
        logger=fake_logger,
    )

    response = await controller.delete_user(
        request=create_request(user_id=8),
        current_user=CurrentUser(user_id=8),
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_controller_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    service_response = DeleteUserResponseDTO(
        success=True,
        message="Deleted with default dependencies.",
        deleted_user_id=8,
    )

    fake_service = Service(response=service_response)
    fake_policy = Policy(authorized=True)

    monkeypatch.setattr(
        "app.routes.delete.user.controllers.controller.DeleteUserService",
        lambda: fake_service,
    )

    monkeypatch.setattr(
        "app.routes.delete.user.controllers.controller.UserPolicy",
        lambda: fake_policy,
    )

    monkeypatch.setattr(
        "app.routes.delete.user.controllers.controller.LOGGER",
        fake_logger,
    )

    controller = DeleteUserController()

    response = await controller.delete_user(
        request=create_request(user_id=8),
        current_user=CurrentUser(user_id=8),
    )

    assert response.status_code == 200
    assert controller.service is fake_service
    assert controller.policy is fake_policy
    assert controller.logger is fake_logger
