import pytest

from app.database.repository import DatabaseRepository

from tests.app.database.repository_helpers import (
    Connection,
    Session,
)


class History:
    def __init__(self, id=None):
        self.id = id


@pytest.mark.asyncio
async def test_save_history_success(fake_logger):
    history = History(id=1)

    repository = DatabaseRepository(
        db_connection=Connection(session=Session()),
        logger=fake_logger,
    )

    result = await repository.save_history(history)

    assert result == 1


@pytest.mark.asyncio
async def test_save_history_assigns_id_when_missing(
    fake_logger,
):
    history = History()

    repository = DatabaseRepository(
        db_connection=Connection(session=Session()),
        logger=fake_logger,
    )

    result = await repository.save_history(history)

    assert result == 10


@pytest.mark.asyncio
async def test_save_history_returns_none_on_commit_error(
    fake_logger,
):
    history = History(id=1)

    repository = DatabaseRepository(
        db_connection=Connection(session=Session(raises="commit")),
        logger=fake_logger,
    )

    result = await repository.save_history(history)

    assert result is None
