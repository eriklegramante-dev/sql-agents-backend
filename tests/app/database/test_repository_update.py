import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import Connection, Session


@pytest.mark.asyncio
async def test_update_last_login_at_returns_true(fake_logger):
    user = UserTable(id=1)

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(record=user)),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.update_last_login_at(1) is True
    assert user.last_login_at is not None


@pytest.mark.asyncio
async def test_update_last_login_at_returns_false_when_user_missing(
    fake_logger,
):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(record=None)),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.update_last_login_at(1) is False


@pytest.mark.asyncio
async def test_update_last_login_at_returns_false_on_error(
    fake_logger,
):
    session = Session(raises="get")

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.update_last_login_at(1) is False
    assert session.rolled_back is True


@pytest.mark.asyncio
async def test_update_user_returns_user_id(fake_logger):
    user = UserTable(id=1)

    session = Session(record=user)

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.update_user(
        user=user,
        update_data={"name": "Updated Name"},
    )

    assert result == 1
    assert user.name == "Updated Name"


@pytest.mark.asyncio
async def test_update_user_returns_none_when_user_not_found(
    fake_logger,
):
    session = Session(record=None)

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.update_user(
        user=UserTable(id=1),
        update_data={"name": "Updated Name"},
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_user_returns_none_on_error(fake_logger):
    user = UserTable(id=1)

    session = Session(
        record=user,
        raises="commit",
    )

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.update_user(
        user=user,
        update_data={"name": "Updated Name"},
    )

    assert result is None
    assert session.rolled_back is True
