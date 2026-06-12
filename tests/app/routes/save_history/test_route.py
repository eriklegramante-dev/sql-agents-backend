from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.routes.save_history.route import save_history
from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
)


@pytest.mark.asyncio
async def test_save_history_calls_controller_handle():
    request = SaveHistoryRequestDTO(
        title="Test Title",
        message={"content": "test"},
        dataset_id=None,
    )

    current_user = MagicMock()

    with patch(
        "app.routes.save_history.route.SaveHistoryController"
    ) as controller_class:
        controller_instance = AsyncMock()

        controller_class.return_value = controller_instance

        controller_instance.handle.return_value = {
            "success": True,
            "message": "History saved successfully.",
            "history_id": None,
        }

        await save_history(
            request=request,
            current_user=current_user,
        )

        controller_class.assert_called_once()

        controller_instance.handle.assert_awaited_once_with(
            request=request,
            current_user=current_user,
        )


@pytest.mark.asyncio
async def test_save_history_returns_controller_response():
    request = SaveHistoryRequestDTO(
        title="Test Title",
        message={"content": "test"},
        dataset_id=None,
    )

    current_user = MagicMock()

    expected_response = {
        "success": True,
        "message": "History saved successfully.",
        "history_id": None,
    }

    with patch(
        "app.routes.save_history.route.SaveHistoryController"
    ) as controller_class:
        controller_instance = AsyncMock()

        controller_class.return_value = controller_instance

        controller_instance.handle.return_value = expected_response

        result = await save_history(
            request=request,
            current_user=current_user,
        )

        assert result == expected_response
