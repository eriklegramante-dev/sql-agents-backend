from types import SimpleNamespace

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.database.repository import DatabaseRepository
from app.models.users_table import UserTable


class BeginContext:
    def __init__(self, raises=False):
        self.raises = raises

    async def __aenter__(self):
        if self.raises:
            raise SQLAlchemyError("boom")
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def run_sync(self, callback):
        self.callback = callback


class Engine:
    def __init__(self, raises=False):
        self.raises = raises

    def begin(self):
        return BeginContext(raises=self.raises)


class Session:
    def __init__(self, record=None, execute_result=None, raises=None):
        self.record = record
        self.execute_result = execute_result
        self.raises = raises
        self.committed = False
        self.rolled_back = False
        self.deleted = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def add(self, instance):
        self.instance = instance

    async def commit(self):
        if self.raises == "commit":
            raise SQLAlchemyError("boom")
        self.committed = True

    async def refresh(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = 10

    async def rollback(self):
        self.rolled_back = True

    async def get(self, model, record_id):
        if self.raises == "get":
            raise SQLAlchemyError("boom")
        return self.record

    async def execute(self, statement):
        if self.raises == "execute":
            raise SQLAlchemyError("boom")
        return self.execute_result


class Result:
    def __init__(self, record):
        self.record = record

    def scalar_one_or_none(self):
        return self.record


class Connection:
    def __init__(self, session=None, engine=None):
        self.session = session
        self.engine = engine or Engine()

    def get_session(self):
        return lambda: self.session


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


@pytest.mark.asyncio
async def test_get_by_id_returns_record(fake_logger):
    record = UserTable(id=1)
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(record=record)),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.get_by_id(1) is record


@pytest.mark.asyncio
async def test_get_by_id_returns_none_on_error(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(raises="get")),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.get_by_id(1) is None


@pytest.mark.asyncio
async def test_get_user_by_email_returns_user(fake_logger):
    user = UserTable(id=1, email="user@example.com")
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(execute_result=Result(user))),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.get_user_by_email("user@example.com") is user


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
async def test_update_last_login_at_returns_false_when_user_missing(fake_logger):
    repository = DatabaseRepository(
        db_connection=Connection(session=Session(record=None)),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.update_last_login_at(1) is False


@pytest.mark.asyncio
async def test_update_last_login_at_returns_false_on_error(fake_logger):
    session = Session(raises="get")
    repository = DatabaseRepository(
        db_connection=Connection(session=session),
        logger=fake_logger,
        model=UserTable,
    )

    assert await repository.update_last_login_at(1) is False
    assert session.rolled_back is True
