import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import (
    Connection,
    Result,
    Session,
)


@pytest.mark.asyncio
async def test_read_user_returns_users(fake_logger):
    users = [
        UserTable(id=1),
        UserTable(id=2),
    ]

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result(users))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.read_user({})

    assert result == users


@pytest.mark.asyncio
async def test_read_user_returns_empty_list(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result([]))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.read_user({})

    assert result == []


@pytest.mark.asyncio
async def test_read_user_returns_none_on_error(
    fake_logger,
):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(raises="execute")),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.read_user({"id": 1})

    assert result is None


@pytest.mark.asyncio
async def test_read_user_applies_filters(fake_logger):
    user = UserTable(
        id=1,
        email="user@test.com",
    )

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result([user]))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.read_user(
        {
            "id": 1,
            "email": "user@test.com",
        }
    )

    assert result == [user]
