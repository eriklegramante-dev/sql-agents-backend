from unittest.mock import AsyncMock

import pytest

from app.core.recent_history.workflow import RecentHistoryWorkflow
from app.models.history_table import HistoryTable


pytestmark = pytest.mark.asyncio


async def test_execute_returns_repository_recent_history(fake_logger):
    history_entries = [HistoryTable(user_id=1, title="Query 1")]
    repository = AsyncMock()
    repository.get_recent_history_by_user_id.return_value = history_entries

    workflow = RecentHistoryWorkflow(
        history_repository=repository,
        logger=fake_logger,
    )

    result = await workflow.execute(user_id=1, limit=3)

    repository.get_recent_history_by_user_id.assert_awaited_once_with(
        user_id=1,
        limit=3,
    )
    assert result == history_entries


async def test_execute_returns_empty_list_when_repository_returns_none(fake_logger):
    repository = AsyncMock()
    repository.get_recent_history_by_user_id.return_value = None

    workflow = RecentHistoryWorkflow(
        history_repository=repository,
        logger=fake_logger,
    )

    result = await workflow.execute(user_id=1)

    assert result == []


async def test_execute_uses_default_limit(fake_logger):
    repository = AsyncMock()
    repository.get_recent_history_by_user_id.return_value = []

    workflow = RecentHistoryWorkflow(
        history_repository=repository,
        logger=fake_logger,
    )

    await workflow.execute(user_id=9)

    repository.get_recent_history_by_user_id.assert_awaited_once_with(
        user_id=9,
        limit=5,
    )


async def test_workflow_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    repository = AsyncMock()
    repository.get_recent_history_by_user_id.return_value = []

    monkeypatch.setattr("app.core.recent_history.workflow.LOGGER", fake_logger)
    monkeypatch.setattr(
        "app.core.recent_history.workflow.DatabaseRepository",
        lambda model: repository,
    )

    workflow = RecentHistoryWorkflow()

    result = await workflow.execute(user_id=1)

    assert result == []
    assert workflow.logger is fake_logger
