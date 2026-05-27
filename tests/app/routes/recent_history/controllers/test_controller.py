import pytest

from app.models.users_table import UserTable
from app.routes.recent_history.controllers.controller import RecentHistoryController
from app.routes.recent_history.dtos.dto import RecentHistoryResponseDTO


pytestmark = pytest.mark.asyncio


class ServiceSuccess:
    def __init__(self):
        self.called_with_user_id = None

    async def handle_recent_history(self, user_id):
        self.called_with_user_id = user_id
        return RecentHistoryResponseDTO(
            success=True,
            message="ok",
            data=[],
        )


class ServiceFailure:
    async def handle_recent_history(self, user_id):
        return RecentHistoryResponseDTO(
            success=False,
            message="failed",
            data=[],
        )


class ServiceError:
    async def handle_recent_history(self, user_id):
        raise RuntimeError("boom")


async def test_get_recent_history_returns_service_response(fake_logger):
    service = ServiceSuccess()
    controller = RecentHistoryController(service=service, logger=fake_logger)

    response = await controller.get_recent_history(UserTable(id=3))

    assert response.success is True
    assert response.message == "ok"
    assert response.data == []
    assert service.called_with_user_id == 3


async def test_get_recent_history_returns_service_failure_response(fake_logger):
    controller = RecentHistoryController(
        service=ServiceFailure(),
        logger=fake_logger,
    )

    response = await controller.get_recent_history(UserTable(id=3))

    assert response.success is False
    assert response.message == "failed"
    assert response.data == []


async def test_get_recent_history_returns_internal_error_response(fake_logger):
    controller = RecentHistoryController(
        service=ServiceError(),
        logger=fake_logger,
    )

    response = await controller.get_recent_history(UserTable(id=3))

    assert response.success is False
    assert response.message == "Internal server error."
    assert response.data == []


async def test_controller_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    service = ServiceSuccess()

    monkeypatch.setattr(
        "app.routes.recent_history.controllers.controller.LOGGER",
        fake_logger,
    )
    monkeypatch.setattr(
        "app.routes.recent_history.controllers.controller.RecentHistoryService",
        lambda: service,
    )

    controller = RecentHistoryController()

    response = await controller.get_recent_history(UserTable(id=1))

    assert response.success is True
    assert controller.logger is fake_logger
    assert service.called_with_user_id == 1
