import pytest

from app.database import connection
from app.database.connection import DatabaseConnection


class Settings:
    class Database:
        def get_current_url(self):
            return "postgresql+asyncpg://user:pass@localhost/db"

    database = Database()


class Engine:
    def __init__(self):
        self.disposed = False

    async def dispose(self):
        self.disposed = True


def test_database_connection_initializes_engine_and_sessionmaker(monkeypatch, fake_logger):
    engine = Engine()
    values = {}

    def create_engine(url, echo, future):
        values["url"] = url
        values["echo"] = echo
        values["future"] = future
        return engine

    def create_sessionmaker(**kwargs):
        values["sessionmaker"] = kwargs
        return "sessionmaker"

    monkeypatch.setattr(connection, "create_async_engine", create_engine)
    monkeypatch.setattr(connection, "async_sessionmaker", create_sessionmaker)

    db_connection = DatabaseConnection(logger=fake_logger, settings=Settings())

    assert values["url"] == "postgresql+asyncpg://user:pass@localhost/db"
    assert db_connection.get_session() == "sessionmaker"


@pytest.mark.asyncio
async def test_database_connection_closes_engine(monkeypatch, fake_logger):
    engine = Engine()

    monkeypatch.setattr(connection, "create_async_engine", lambda *args, **kwargs: engine)
    monkeypatch.setattr(connection, "async_sessionmaker", lambda **kwargs: "sessionmaker")

    db_connection = DatabaseConnection(logger=fake_logger, settings=Settings())
    await db_connection.close()

    assert engine.disposed is True
