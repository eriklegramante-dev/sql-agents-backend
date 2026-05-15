import pytest

from app.routes.update.dtos.dto import UpdateUserRequestDTO
from app.routes.update.services.service import UpdateUserService


class WorkflowSuccess:
    async def run(self, request):
        return {"success": True, "message": "updated", "data": {"id": 1}}


class WorkflowValueError:
    async def run(self, request):
        raise ValueError("invalid")


class WorkflowError:
    async def run(self, request):
        raise RuntimeError("boom")


def update_request() -> UpdateUserRequestDTO:
    return UpdateUserRequestDTO(
        id=1,
        name="Updated User",
        password="Strong@123",  # pragma: allowlist secret
    )


@pytest.mark.asyncio
async def test_handle_update_returns_workflow_response(fake_logger):
    service = UpdateUserService(workflow=WorkflowSuccess(), logger=fake_logger)

    response = await service.handle_update(update_request())

    assert response.success is True
    assert response.data == {"id": 1}


@pytest.mark.asyncio
async def test_handle_update_propagates_value_error(fake_logger):
    service = UpdateUserService(workflow=WorkflowValueError(), logger=fake_logger)

    with pytest.raises(ValueError, match="invalid"):
        await service.handle_update(update_request())


@pytest.mark.asyncio
async def test_handle_update_propagates_unexpected_error(fake_logger):
    service = UpdateUserService(workflow=WorkflowError(), logger=fake_logger)

    with pytest.raises(RuntimeError, match="boom"):
        await service.handle_update(update_request())
