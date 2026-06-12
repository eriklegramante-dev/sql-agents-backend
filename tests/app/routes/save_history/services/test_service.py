from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.routes.save_history.services.service import (
    SaveHistoryService,
)
from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
    SaveHistoryResponseDTO,
)
from app.models.users_table import UserTable


@pytest.mark.asyncio
async def test_handle_save_history_returns_response_dto():
    workflow = AsyncMock()

    history_id = uuid4()

    workflow.execute.return_value = {
        "success": True,
        "message": "History saved successfully.",
        "history_id": history_id,
    }

    service = SaveHistoryService(
        workflow=workflow,
    )

    request = SaveHistoryRequestDTO(
        title="Test Title",
        message={"text": "hello"},
        dataset_id=uuid4(),
    )

    current_user = UserTable()
    current_user.id = 10

    result = await service.handle_save_history(
        request=request,
        current_user=current_user,
    )

    assert isinstance(
        result,
        SaveHistoryResponseDTO,
    )

    assert result.success is True
    assert result.message == "History saved successfully."
    assert result.history_id == history_id


@pytest.mark.asyncio
async def test_handle_save_history_calls_workflow_with_correct_arguments():
    workflow = AsyncMock()

    workflow.execute.return_value = {
        "success": True,
        "message": "History saved successfully.",
        "history_id": uuid4(),
    }

    service = SaveHistoryService(
        workflow=workflow,
    )

    request = SaveHistoryRequestDTO(
        title="My History",
        message={"content": "test"},
        dataset_id=uuid4(),
    )

    current_user = UserTable()
    current_user.id = 50

    await service.handle_save_history(
        request=request,
        current_user=current_user,
    )

    workflow.execute.assert_awaited_once_with(
        request=request,
        current_user=current_user,
    )


@pytest.mark.asyncio
async def test_handle_save_history_returns_failure_response():
    workflow = AsyncMock()

    workflow.execute.return_value = {
        "success": False,
        "message": "Failed to save history.",
        "history_id": None,
    }

    service = SaveHistoryService(
        workflow=workflow,
    )

    request = SaveHistoryRequestDTO(
        title="Failed History",
        message={"content": "test"},
        dataset_id=None,
    )

    current_user = UserTable()
    current_user.id = 1

    result = await service.handle_save_history(
        request=request,
        current_user=current_user,
    )

    assert result.success is False
    assert result.message == "Failed to save history."
    assert result.history_id is None


def test_init_uses_injected_dependencies():
    workflow = MagicMock()
    logger = MagicMock()

    service = SaveHistoryService(
        workflow=workflow,
        logger=logger,
    )

    assert service.workflow is workflow
    assert service.logger is logger


def test_init_uses_default_dependencies():
    service = SaveHistoryService()

    assert service.workflow is not None
    assert service.logger is not None
