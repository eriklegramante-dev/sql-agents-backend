import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import Connection, Engine


@pytest.mark.asyncio
async def test_create_tables_returns_true(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(engine=Engine()),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.create_tables() is True


@pytest.mark.asyncio
async def test_create_tables_returns_false_on_error(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(engine=Engine(raises=True)),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.create_tables() is False
