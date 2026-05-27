import pytest

from app.database.repository import DatabaseRepository
from app.models.chat_history_table import ChatHistoryTable

from tests.app.database.repository_helpers import Connection, Result, Session


@pytest.mark.asyncio
async def test_delete_oldest_chat_history_returns_deleted_history(fake_logger):
    history = ChatHistoryTable(id=1, user_id=1, message="First message")

    session = Session(execute_result=Result(history))

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=ChatHistoryTable,
    )

    result = await repository.delete_oldest_chat_history_by_user_id(user_id=1)

    assert result is history
    assert session.deleted is history
    assert session.committed is True


@pytest.mark.asyncio
async def test_delete_oldest_chat_history_returns_none_when_not_found(
    fake_logger,
):
    session = Session(execute_result=Result(None))

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=ChatHistoryTable,
    )

    result = await repository.delete_oldest_chat_history_by_user_id(user_id=1)

    assert result is None
    assert session.deleted is None
    assert session.committed is False


@pytest.mark.asyncio
async def test_delete_oldest_chat_history_returns_none_on_execute_error(
    fake_logger,
):
    session = Session(raises="execute")

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=ChatHistoryTable,
    )

    result = await repository.delete_oldest_chat_history_by_user_id(user_id=1)

    assert result is None
    assert session.rolled_back is True


@pytest.mark.asyncio
async def test_delete_oldest_chat_history_returns_none_on_delete_error(
    fake_logger,
):
    history = ChatHistoryTable(id=1, user_id=1, message="First message")

    session = Session(
        execute_result=Result(history),
        raises="delete",
    )

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=ChatHistoryTable,
    )

    result = await repository.delete_oldest_chat_history_by_user_id(user_id=1)

    assert result is None
    assert session.rolled_back is True
