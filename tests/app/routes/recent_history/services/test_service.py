from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.history_table import HistoryStatus
from app.routes.recent_history.services.service import RecentHistoryService


pytestmark = pytest.mark.asyncio


class WorkflowSuccess:
    def __init__(self, entries):
        self.entries = entries
        self.called_with_user_id = None

    async def execute(self, user_id):
        self.called_with_user_id = user_id
        return self.entries


class WorkflowError:
    async def execute(self, user_id):
        raise RuntimeError("boom")


def history_entry(**overrides):
    values = {
        "id": uuid4(),
        "dataset_id": uuid4(),
        "title": "Sales report",
        "status": HistoryStatus.ACTIVE,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


async def test_handle_recent_history_returns_success_response(fake_logger):
    entry = history_entry()
    workflow = WorkflowSuccess([entry])
    service = RecentHistoryService(workflow=workflow, logger=fake_logger)

    response = await service.handle_recent_history(user_id=7)

    assert response.success is True
    assert response.message == "Recent history retrieved successfully."
    assert workflow.called_with_user_id == 7
    assert len(response.data) == 1
    assert response.data[0].id == entry.id
    assert response.data[0].dataset_id == entry.dataset_id
    assert response.data[0].status == "ACTIVE"


async def test_handle_recent_history_returns_empty_success_response(fake_logger):
    service = RecentHistoryService(
        workflow=WorkflowSuccess([]),
        logger=fake_logger,
    )

    response = await service.handle_recent_history(user_id=7)

    assert response.success is True
    assert response.data == []


async def test_handle_recent_history_returns_failure_response_on_error(fake_logger):
    service = RecentHistoryService(workflow=WorkflowError(), logger=fake_logger)

    response = await service.handle_recent_history(user_id=7)

    assert response.success is False
    assert response.message == "Failed to retrieve recent history."
    assert response.data == []


async def test_service_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    workflow = WorkflowSuccess([])

    monkeypatch.setattr(
        "app.routes.recent_history.services.service.LOGGER", fake_logger
    )
    monkeypatch.setattr(
        "app.routes.recent_history.services.service.RecentHistoryWorkflow",
        lambda: workflow,
    )

    service = RecentHistoryService()

    response = await service.handle_recent_history(user_id=1)

    assert response.success is True
    assert service.logger is fake_logger
    assert workflow.called_with_user_id == 1
