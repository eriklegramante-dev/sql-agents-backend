import pytest
from fastapi.responses import JSONResponse

from app.routes.delete.history.controllers.controller import (
    DeleteHistoryController,
)
from app.routes.delete.history.dtos.dto import (
    DeleteHistoryResponseDTO,
)


class CurrentUser:
    def __init__(self, user_id=1):
        self.id = user_id


class Service:
    def __init__(self, response=None, raises=False):
        self.response = response
        self.raises = raises
        self.current_user = None

    async def handle_delete(self, current_user):
        if self.raises:
            raise RuntimeError("boom")

        self.current_user = current_user
        return self.response


@pytest.mark.asyncio
async def test_delete_history_returns_success_response(fake_logger):
    service_response = DeleteHistoryResponseDTO(
        success=True,
        message="Chat history deleted successfully.",
        data={"deleted_history_id": 1},
    )

    service = Service(response=service_response)

    controller = DeleteHistoryController(
        service=service,
        logger=fake_logger,
    )

    response = await controller.delete_history(
        current_user=CurrentUser(user_id=1),
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert service.current_user.id == 1


@pytest.mark.asyncio
async def test_delete_history_returns_not_found_response(fake_logger):
    service_response = DeleteHistoryResponseDTO(
        success=False,
        message="Chat history not found or could not be deleted.",
        data=None,
    )

    controller = DeleteHistoryController(
        service=Service(response=service_response),
        logger=fake_logger,
    )

    response = await controller.delete_history(
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_history_returns_unauthorized_when_user_is_missing(
    fake_logger,
):
    controller = DeleteHistoryController(
        service=Service(),
        logger=fake_logger,
    )

    response = await controller.delete_history(
        current_user=None,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_history_returns_internal_server_error(fake_logger):
    controller = DeleteHistoryController(
        service=Service(raises=True),
        logger=fake_logger,
    )

    response = await controller.delete_history(
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 500


@pytest.mark.asyncio
async def test_controller_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    service_response = DeleteHistoryResponseDTO(
        success=True,
        message="Deleted with default dependencies.",
        data={"deleted_history_id": 1},
    )

    fake_service = Service(response=service_response)

    monkeypatch.setattr(
        "app.routes.delete.history.controllers.controller.DeleteHistoryService",
        lambda: fake_service,
    )

    monkeypatch.setattr(
        "app.routes.delete.history.controllers.controller.LOGGER",
        fake_logger,
    )

    controller = DeleteHistoryController()

    response = await controller.delete_history(
        current_user=CurrentUser(user_id=1),
    )

    assert response.status_code == 200
    assert controller.service is fake_service
    assert controller.logger is fake_logger
