import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import Connection, Result, Session


@pytest.mark.asyncio
async def test_delete_user_returns_deleted_user(fake_logger):
    user = UserTable(id=1, email="user@example.com")

    session = Session(execute_result=Result(user))

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.delete_user({"email": "user@example.com"})

    assert result is user
    assert session.deleted is user
    assert session.committed is True


@pytest.mark.asyncio
async def test_delete_user_returns_none_when_user_not_found(fake_logger):
    session = Session(execute_result=Result(None))

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.delete_user({"email": "missing@example.com"})

    assert result is None
    assert session.deleted is None
    assert session.committed is False


@pytest.mark.asyncio
async def test_delete_user_returns_none_on_execute_error(fake_logger):
    session = Session(raises="execute")

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.delete_user({"email": "user@example.com"})

    assert result is None
    assert session.rolled_back is True


@pytest.mark.asyncio
async def test_delete_user_returns_none_on_delete_error(fake_logger):
    user = UserTable(id=1, email="user@example.com")

    session = Session(
        execute_result=Result(user),
        raises="delete",
    )

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.delete_user({"email": "user@example.com"})

    assert result is None
    assert session.rolled_back is True
