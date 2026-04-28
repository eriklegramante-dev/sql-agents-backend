import pytest

from app.routes.auth.dtos.dto import LoginRequestDTO
from app.routes.auth.services.service import LoginService


class WorkflowSuccess:
    async def run(self, request):
        return {
            "success": True,
            "message": "Login successful.",
            "access_token": "token",
            "token_type": "bearer",
        }


class WorkflowValueError:
    async def run(self, request):
        raise ValueError("invalid")


class WorkflowError:
    async def run(self, request):
        raise RuntimeError("boom")


def login_request() -> LoginRequestDTO:
    return LoginRequestDTO(username="user@example.com", password="Strong@123")


@pytest.mark.asyncio
async def test_handle_login_returns_workflow_response(fake_logger):
    service = LoginService(workflow=WorkflowSuccess(), logger=fake_logger)

    response = await service.handle_login(login_request())

    assert response.success is True
    assert response.access_token == "token"


@pytest.mark.asyncio
async def test_handle_login_propagates_value_error(fake_logger):
    service = LoginService(workflow=WorkflowValueError(), logger=fake_logger)

    with pytest.raises(ValueError, match="invalid"):
        await service.handle_login(login_request())


@pytest.mark.asyncio
async def test_handle_login_propagates_unexpected_error(fake_logger):
    service = LoginService(workflow=WorkflowError(), logger=fake_logger)

    with pytest.raises(RuntimeError, match="boom"):
        await service.handle_login(login_request())
