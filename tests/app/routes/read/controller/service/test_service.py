import pytest

from app.routes.read.services.services import (
    ReadUserService,
)


class WorkflowSuccess:
    async def run(self, request, current_user):
        return {
            "success": True,
            "message": "success",
            "data": []
        }


class WorkflowError:
    async def run(self, request, current_user):
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_should_return_workflow_response(fake_logger):

    service = ReadUserService(
        workflow=WorkflowSuccess(),
        logger=fake_logger,
    )

    response = await service.handle_read(
        request=object(),
        current_user=object(),
    )

    assert response.success is True


@pytest.mark.asyncio
async def test_should_raise_runtime_error(fake_logger):

    service = ReadUserService(
        workflow=WorkflowError(),
        logger=fake_logger,
    )

    with pytest.raises(RuntimeError):

        await service.handle_read(
            request=object(),
            current_user=object(),
        )