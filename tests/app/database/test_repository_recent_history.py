from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database.repository import DatabaseRepository
from app.models.history_table import HistoryStatus, HistoryTable
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
@pytest.mark.parametrize("user_id, limit", [(7, 3), (42, 8)])
async def test_get_recent_history_by_user_id_filters_orders_and_limits_query(
    fake_logger, user_id, limit
):
    session = Session(execute_result=RecentHistoryResult([]))
    session.execute = AsyncMock(wraps=session.execute)
    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=HistoryTable,
    )

    await repository.get_recent_history_by_user_id(user_id=user_id, limit=limit)

    session.execute.assert_awaited_once()
    query = session.execute.await_args.args[0]
    expected_query = (
        select(HistoryTable)
        .where(
            HistoryTable.user_id == user_id,
            HistoryTable.status != HistoryStatus.DELETED,
        )
        .order_by(HistoryTable.created_at.desc(), HistoryTable.id.desc())
        .limit(limit)
    )
    assert query.compare(expected_query)


@pytest.mark.asyncio
async def test_get_recent_history_by_user_id_returns_entries(fake_logger):
    history_entries = [
        HistoryTable(user_id=1, title="New query", status=HistoryStatus.ACTIVE),
        HistoryTable(
            user_id=1, title="Previous query", status=HistoryStatus.ARCHIVED
        ),
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
async def test_get_recent_history_by_user_id_propagates_query_error(
    fake_logger,
):
    error = SQLAlchemyError("query failed")
    session = Session()
    session.execute = AsyncMock(side_effect=error)
    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=HistoryTable,
    )

    with pytest.raises(SQLAlchemyError, match="query failed") as exc_info:
        await repository.get_recent_history_by_user_id(user_id=1)

    assert exc_info.value is error
    session.execute.assert_awaited_once()
