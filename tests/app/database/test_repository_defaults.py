from types import SimpleNamespace

import pytest

from app.database.repository import DatabaseRepository

from tests.app.database.repository_helpers import Session


@pytest.mark.asyncio
async def test_repository_uses_default_dependencies_with_monkeypatch(
    monkeypatch,
    fake_logger,
):
    session = Session()

    class FakeDatabaseConnection:
        def __init__(self, logger):
            self.logger = logger

        def get_session(self):
            return lambda: session

    monkeypatch.setattr("app.database.repository.LOGGER", fake_logger)
    monkeypatch.setattr(
        "app.database.repository.DatabaseConnection",
        FakeDatabaseConnection,
    )

    repository = DatabaseRepository()

    result = await repository.insert(SimpleNamespace(id=None))

    assert result == 10
    assert repository.logger is fake_logger
