from datetime import date

import pytest

from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.admin.services.service import CreateAdminService


class WorkflowSuccess:
    async def run(self, request):
        return {"success": True, "message": "created", "data": {"id": 1}}


class WorkflowValueError:
    async def run(self, request):
        raise ValueError("invalid")


class WorkflowError:
    async def run(self, request):
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


@pytest.mark.asyncio
async def test_handle_create_returns_workflow_response(fake_logger):
    service = CreateAdminService(workflow=WorkflowSuccess(), logger=fake_logger)

    response = await service.handle_create(create_request())

    assert response.success is True
    assert response.data == {"id": 1}


@pytest.mark.asyncio
async def test_handle_create_propagates_value_error(fake_logger):
    service = CreateAdminService(workflow=WorkflowValueError(), logger=fake_logger)

    with pytest.raises(ValueError, match="invalid"):
        await service.handle_create(create_request())


@pytest.mark.asyncio
async def test_handle_create_propagates_unexpected_error(fake_logger):
    service = CreateAdminService(workflow=WorkflowError(), logger=fake_logger)

    with pytest.raises(RuntimeError, match="boom"):
        await service.handle_create(create_request())
