import pytest

from app.database.repository import DatabaseRepository
from app.models.history_table import HistoryTable
from tests.app.database.repository_helpers import Connection, Session


class Scalars:
    def __init__(self, records):
        self.records = records

    def all(self):
        return self.records


class RecentHistoryResult:
    def __init__(self, records):
        self.records = records

    def scalars(self):
        return Scalars(self.records)


@pytest.mark.asyncio
async def test_get_recent_history_by_user_id_returns_entries(fake_logger):
    history_entries = [
        HistoryTable(user_id=1, title="New query"),
        HistoryTable(user_id=1, title="Previous query"),
    ]

    repository = DatabaseRepository(
        db_connection=Connection(
            session=Session(execute_result=RecentHistoryResult(history_entries))
        ),
        logger=fake_logger,
        model=HistoryTable,
    )

    result = await repository.get_recent_history_by_user_id(user_id=1, limit=2)

    assert result == history_entries


@pytest.mark.asyncio
async def test_get_recent_history_by_user_id_returns_empty_list(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(
            session=Session(execute_result=RecentHistoryResult([]))
        ),
        logger=fake_logger,
        model=HistoryTable,
    )

    result = await repository.get_recent_history_by_user_id(user_id=1)

    assert result == []


@pytest.mark.asyncio
async def test_get_recent_history_by_user_id_returns_empty_list_on_error(
    fake_logger,
):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(raises="execute")),
        logger=fake_logger,
        model=HistoryTable,
    )

    result = await repository.get_recent_history_by_user_id(user_id=1)

    assert result == []
