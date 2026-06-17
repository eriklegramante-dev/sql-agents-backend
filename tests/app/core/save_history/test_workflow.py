from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.save_history.workflow import SaveHistoryWorkflow
from app.models.history_table import HistoryStatus
from app.models.users_table import UserTable
from app.routes.save_history.dtos.dto import SaveHistoryRequestDTO


@pytest.mark.asyncio
async def test_execute_returns_success():
    repository = AsyncMock()

    history_id = uuid4()

    repository.save_history.return_value = history_id

    workflow = SaveHistoryWorkflow(
        repository=repository,
    )

    request = SaveHistoryRequestDTO(
        dataset_id=uuid4(),
        title="Test Title",
        message={
            "role": "user",
            "content": "Test Message",
        },
    )

    current_user = UserTable()
    current_user.id = 10

    result = await workflow.execute(
        request=request,
        current_user=current_user,
    )

    assert result == {
        "success": True,
        "message": "History saved successfully.",
        "data": {
            "history_id": history_id,
        },
    }

    repository.save_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_returns_failure_when_history_is_not_saved():
    repository = AsyncMock()

    repository.save_history.return_value = None

    workflow = SaveHistoryWorkflow(
        repository=repository,
    )

    request = SaveHistoryRequestDTO(
        dataset_id=uuid4(),
        title="Test Title",
        message={
            "role": "user",
            "content": "Test Message",
        },
    )

    current_user = UserTable()
    current_user.id = 10

    result = await workflow.execute(
        request=request,
        current_user=current_user,
    )

    assert result == {
        "success": False,
        "message": "Failed to save history.",
        "data": {
            "history_id": None,
        },
    }

    repository.save_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_execute_builds_history_entity_correctly():
    repository = AsyncMock()

    repository.save_history.return_value = uuid4()

    workflow = SaveHistoryWorkflow(
        repository=repository,
    )

    dataset_id = uuid4()

    payload = {
        "role": "user",
        "content": "History Message",
    }

    request = SaveHistoryRequestDTO(
        dataset_id=dataset_id,
        title="History Title",
        message=payload,
    )

    current_user = UserTable()
    current_user.id = 50

    await workflow.execute(
        request=request,
        current_user=current_user,
    )

    history = repository.save_history.call_args.args[0]

    assert history.user_id == 50
    assert history.dataset_id == dataset_id
    assert history.title == "History Title"
    assert history.message == payload
    assert history.status == HistoryStatus.ACTIVE


def test_init_uses_injected_dependencies():
    repository = MagicMock()

    logger = MagicMock()

    workflow = SaveHistoryWorkflow(
        repository=repository,
        logger=logger,
    )

    assert workflow.repository is repository
    assert workflow.logger is logger
