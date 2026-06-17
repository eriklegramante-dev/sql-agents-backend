from unittest.mock import AsyncMock, MagicMock
import json

import pytest
from fastapi.responses import JSONResponse

from app.routes.save_history.controllers.controller import (
    SaveHistoryController,
)
from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
    SaveHistoryResponseDTO,
)
from app.models.users_table import UserTable


@pytest.mark.asyncio
async def test_handle_returns_json_response():
    service = AsyncMock()

    service.handle_save_history.return_value = SaveHistoryResponseDTO(
        success=True,
        message="History saved successfully.",
        data={
            "history_id": None,
        },
    )

    controller = SaveHistoryController(
        service=service,
    )

    request = SaveHistoryRequestDTO(
        title="History Title",
        message={"text": "hello"},
        dataset_id=None,
    )

    current_user = UserTable()
    current_user.id = 1

    response = await controller.handle(
        request=request,
        current_user=current_user,
    )

    assert isinstance(response, JSONResponse)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_handle_calls_service_with_correct_arguments():
    service = AsyncMock()

    service.handle_save_history.return_value = SaveHistoryResponseDTO(
        success=True,
        message="History saved successfully.",
        data={
            "history_id": None,
        },
    )

    controller = SaveHistoryController(
        service=service,
    )

    request = SaveHistoryRequestDTO(
        title="History Title",
        message={"text": "hello"},
        dataset_id=None,
    )

    current_user = UserTable()
    current_user.id = 10

    await controller.handle(
        request=request,
        current_user=current_user,
    )

    service.handle_save_history.assert_awaited_once_with(
        request=request,
        current_user=current_user,
    )


@pytest.mark.asyncio
async def test_handle_returns_expected_content():
    service = AsyncMock()

    service.handle_save_history.return_value = SaveHistoryResponseDTO(
        success=True,
        message="History saved successfully.",
        data={
            "history_id": None,
        },
    )

    controller = SaveHistoryController(
        service=service,
    )

    request = SaveHistoryRequestDTO(
        title="History Title",
        message={"text": "hello"},
        dataset_id=None,
    )

    current_user = UserTable()
    current_user.id = 1

    response = await controller.handle(
        request=request,
        current_user=current_user,
    )

    content = json.loads(response.body)

    assert content == {
        "success": True,
        "message": "History saved successfully.",
        "data": {
            "history_id": None,
        },
    }


def test_init_uses_injected_dependencies():
    service = MagicMock()
    logger = MagicMock()

    controller = SaveHistoryController(
        service=service,
        logger=logger,
    )

    assert controller.service is service
    assert controller.logger is logger


def test_init_uses_default_dependencies():
    controller = SaveHistoryController()

    assert controller.service is not None
    assert controller.logger is not None
