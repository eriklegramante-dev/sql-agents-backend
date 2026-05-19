import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import Connection, Result, Session


@pytest.mark.asyncio
async def test_search_user_by_filters_with_id(fake_logger):
    user = UserTable(id=1)

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result(user))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.search_user_by_filters(id=1)

    assert result is user


@pytest.mark.asyncio
async def test_search_user_by_filters_with_email(fake_logger):
    user = UserTable(id=1, email="user@example.com")

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result(user))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.search_user_by_filters(email="user@example.com")

    assert result is user


@pytest.mark.asyncio
async def test_search_user_by_filters_with_cpf(fake_logger):
    user = UserTable(id=1)

    user.cpf = "12345678900"

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result(user))),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.search_user_by_filters(cpf="12345678900")

    assert result is user


@pytest.mark.asyncio
async def test_search_user_by_filters_returns_none_on_error(
    fake_logger,
):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(raises="execute")),
        logger=fake_logger,
        model=UserTable,
    )

    result = await repository.search_user_by_filters(id=1)

    assert result is None
