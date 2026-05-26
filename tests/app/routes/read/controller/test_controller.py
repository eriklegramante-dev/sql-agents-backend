import pytest
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError

from app.routes.read.controllers.controller import (
    ReadUserController,
)

from app.routes.read.dtos.dto import (
    GetUserResponseDTO,
)


pytestmark = pytest.mark.asyncio


class PolicyAllow:
    def can_view(self, request, current_user):
        return True


class PolicyDeny:
    def can_view(self, request, current_user):
        return False


class ServiceSuccess:
    async def handle_read(self, request, current_user):
        return GetUserResponseDTO(
            success=True,
            message="success",
            data=[]
        )


class ServiceError:
    async def handle_read(self, request, current_user):
        raise RuntimeError("boom")


class ServiceValidationError:
    async def handle_read(self, request, current_user):
        raise ValidationError.from_exception_data(
            "GetUserRequestDTO",
            [],
        )


async def test_should_return_200_when_success(fake_logger):

    controller = ReadUserController(
        service=ServiceSuccess(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    response = await controller.handle(
        request=object(),
        current_user=SimpleNamespace(id=1),
    )

    assert response.status_code == 200


async def test_should_return_403_when_not_authorized(fake_logger):

    controller = ReadUserController(
        service=ServiceSuccess(),
        policy=PolicyDeny(),
        logger=fake_logger,
    )

    with pytest.raises(HTTPException) as exc:

        await controller.handle(
            request=object(),
            current_user=SimpleNamespace(id=1),
        )

    assert exc.value.status_code == 403


async def test_should_return_500_when_internal_error(fake_logger):

    controller = ReadUserController(
        service=ServiceError(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    with pytest.raises(HTTPException) as exc:

        await controller.handle(
            request=object(),
            current_user=SimpleNamespace(id=1),
        )

    assert exc.value.status_code == 500


async def test_should_return_400_when_validation_error(fake_logger):

    controller = ReadUserController(
        service=ServiceValidationError(),
        policy=PolicyAllow(),
        logger=fake_logger,
    )

    with pytest.raises(HTTPException) as exc:

        await controller.handle(
            request=object(),
            current_user=SimpleNamespace(id=1),
        )

    assert exc.value.status_code == 400