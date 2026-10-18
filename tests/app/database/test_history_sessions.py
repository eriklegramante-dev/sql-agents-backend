"""Session SQL and API contracts; these tests do not connect to PostgreSQL."""
import json
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects import postgresql

from app.database.history_errors import DeletedHistoryError
from app.database.repository import DatabaseRepository
from app.models.history_table import HistoryTable
from app.models.users_table import UserTable
from app.core.save_history.workflow import SaveHistoryWorkflow
from app.routes.save_history.controllers.controller import SaveHistoryController
from app.routes.save_history.services.service import SaveHistoryService
from app.routes.save_history.dtos.dto import SaveHistoryRequestDTO
from tests.app.database.repository_helpers import Connection, Session, Result


class RecordingSession(Session):
    async def execute(self, statement):
        self.statement = statement
        return await super().execute(statement)

    async def flush(self):
        if self.instance.id is None:
            self.instance.id = uuid4()


@pytest.mark.asyncio
@pytest.mark.parametrize('user_id', [1, 2])
async def test_session_upsert_sql_and_returned_id(fake_logger, user_id):
    saved_id = uuid4()
    session = RecordingSession(execute_result=Result(saved_id))
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    history = HistoryTable(user_id=user_id, session_id=UUID('11111111-1111-1111-1111-111111111111'), title='new',
                           message={'text': 'updated'}, dataset_id=None)
    assert await repository.save_history(history) == saved_id
    compiled = session.statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert 'ON CONFLICT ON CONSTRAINT uq_history_user_session DO UPDATE SET' in sql
    update = sql.split('DO UPDATE SET ')[1].split(' RETURNING')[0]
    assert 'title = excluded.title' in update
    assert 'message = excluded.message' in update
    assert 'dataset_id = excluded.dataset_id' in update
    assert 'updated_at = now()' in update
    assert 'WHERE history.status !=' in update
    assignments = update.split(' WHERE')[0]
    assert 'created_at' not in assignments
    assert 'status =' not in assignments
    assert {item.split(' = ')[0] for item in assignments.split(', ')} == {
        'title', 'message', 'dataset_id', 'updated_at'}
    assert compiled.params['user_id'] == user_id
    assert compiled.params['session_id'] == history.session_id
    assert 'DELETED' in [getattr(v, 'value', v) for v in compiled.params.values()]
    assert session.committed


@pytest.mark.asyncio
async def test_deleted_session_rolls_back(fake_logger):
    session = RecordingSession(execute_result=Result(None))
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    with pytest.raises(DeletedHistoryError):
        await repository.save_history(HistoryTable(user_id=1, session_id=uuid4(),
                                                  title='new', message={}))
    assert session.rolled_back
    assert not session.committed


@pytest.mark.asyncio
@pytest.mark.parametrize('failure', ['execute', 'commit'])
async def test_database_failure_reaches_http_as_failure(fake_logger, failure):
    session = RecordingSession(execute_result=Result(uuid4()), raises=failure)
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    controller = SaveHistoryController(service=SaveHistoryService(
        workflow=SaveHistoryWorkflow(repository=repository, logger=fake_logger)))
    response = await controller.handle(
        SaveHistoryRequestDTO(title='new', message={}, session_id=uuid4()), UserTable(id=7))
    assert response.status_code == 500
    assert json.loads(response.body) == {
        'success': False, 'message': 'Failed to save history.', 'data': {'history_id': None}}
    assert session.rolled_back


@pytest.mark.asyncio
async def test_deleted_session_http_conflict(fake_logger):
    session = RecordingSession(execute_result=Result(None))
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    controller = SaveHistoryController(service=SaveHistoryService(
        workflow=SaveHistoryWorkflow(repository=repository, logger=fake_logger)))
    response = await controller.handle(
        SaveHistoryRequestDTO(title='new', message={}, session_id=uuid4()), UserTable(id=7))
    assert response.status_code == 409
    assert json.loads(response.body)['success'] is False


@pytest.mark.asyncio
async def test_session_and_authenticated_identity_flow_through_route(fake_logger):
    from unittest.mock import patch
    from app.routes.save_history.route import save_history
    repository = AsyncMock()
    repository.save_history.return_value = uuid4()
    controller = SaveHistoryController(service=SaveHistoryService(
        workflow=SaveHistoryWorkflow(repository=repository, logger=fake_logger)))
    request = SaveHistoryRequestDTO(title='new', message={}, session_id=uuid4(), user_id=99)
    user = UserTable(id=7)
    with patch('app.routes.save_history.route.SaveHistoryController', return_value=controller):
        response = await save_history(request=request, current_user=user)
    assert response.status_code == 200
    entity = repository.save_history.call_args.args[0]
    assert entity.user_id == 7
    assert entity.session_id == request.session_id


@pytest.mark.asyncio
async def test_legacy_calls_create_independent_records(fake_logger):
    session = RecordingSession()
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    request = SaveHistoryRequestDTO(title='legacy', message={})
    workflow = SaveHistoryWorkflow(repository=repository, logger=fake_logger)
    first = await workflow.execute(request, UserTable(id=1))
    second = await workflow.execute(request, UserTable(id=1))
    assert first['success'] and second['success']
    assert first['data']['history_id'] != second['data']['history_id']
    assert session.instance.session_id is None
    assert not hasattr(session, 'statement')


def test_session_nullable_and_unique_per_user():
    assert HistoryTable.__table__.c.session_id.nullable
    constraints = [c for c in HistoryTable.__table__.constraints if isinstance(c, UniqueConstraint)]
    assert [(c.name, list(c.columns.keys())) for c in constraints] == [
        ('uq_history_user_session', ['user_id', 'session_id'])]
