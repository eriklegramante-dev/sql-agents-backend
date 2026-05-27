from types import SimpleNamespace

import pytest

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable

from tests.app.database.repository_helpers import Connection, Session


@pytest.mark.asyncio
async def test_insert_returns_record_id(fake_logger):
    session = Session()

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    instance = SimpleNamespace(id=None)

    assert await repository.insert(instance) == 10


@pytest.mark.asyncio
async def test_insert_returns_none_on_error(fake_logger):
    session = Session(raises="commit")

    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.insert(SimpleNamespace(id=None)) is None
    assert session.rolled_back is True
