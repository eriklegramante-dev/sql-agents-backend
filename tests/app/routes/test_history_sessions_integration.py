"""HTTP/layer contracts using real JWT authentication and mocked DB sessions.

No PostgreSQL execution: SQL structure cannot prove concurrent upsert behavior.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.dialects import postgresql

from app.core.chat_sessions.workflow import ChatSessionCountWorkflow
from app.core.recent_history.workflow import RecentHistoryWorkflow
from app.core.save_history.workflow import SaveHistoryWorkflow
from app.database.history_session_repository import HistorySessionRepository
from app.database.repository import DatabaseRepository
from app.models.history_table import HistoryStatus, HistoryTable
from app.models.users_table import UserTable
from app.routes.chat_sessions.controllers.controller import ChatSessionCountController
from app.routes.chat_sessions.services.service import ChatSessionCountService
from app.routes.recent_history.controllers.controller import RecentHistoryController
from app.routes.recent_history.services.service import RecentHistoryService
from app.routes.save_history.controllers.controller import SaveHistoryController
from app.routes.save_history.services.service import SaveHistoryService
from app.routes.router import api_router
from app.security import security
from app.security.authenticator import JWTAuthenticator
from tests.app.database.repository_helpers import Connection, Result, Session


class HistorySession(Session):
    async def flush(self):
        self.instance.id = uuid4()


@pytest.fixture
def history_http(monkeypatch, fake_logger):
    app = FastAPI()
    app.include_router(api_router)
    authenticator = JWTAuthenticator(
        secret_key="history-integration-secret", algorithm="HS256", logger=fake_logger
    )
    users = AsyncMock()
    users.get_by_id.side_effect = lambda user_id: (
        UserTable(id=user_id) if user_id in (7, 8) else None
    )
    monkeypatch.setattr(security, "JWTAuthenticator", lambda: authenticator)
    monkeypatch.setattr(security, "DatabaseRepository", lambda model: users)
    monkeypatch.setattr(security, "LOGGER", fake_logger)
    session = HistorySession()
    session.execute = AsyncMock(wraps=session.execute)
    repository = DatabaseRepository(Connection(session), fake_logger, HistoryTable)
    count_repository = HistorySessionRepository(Connection(session), fake_logger, HistoryTable)
    count_repository.count_sessions_by_user_id = AsyncMock(
        wraps=count_repository.count_sessions_by_user_id
    )
    count_workflow = ChatSessionCountWorkflow(count_repository)
    count_workflow.execute = AsyncMock(wraps=count_workflow.execute)
    count_service = ChatSessionCountService(count_workflow)
    count_service.execute = AsyncMock(wraps=count_service.execute)
    count_controller = ChatSessionCountController(count_service, fake_logger)
    count_controller.execute = AsyncMock(wraps=count_controller.execute)
    save_controller = SaveHistoryController(
        SaveHistoryService(SaveHistoryWorkflow(repository, fake_logger)), fake_logger
    )
    recent_controller = RecentHistoryController(
        service=RecentHistoryService(RecentHistoryWorkflow(repository, fake_logger), fake_logger),
        logger=fake_logger,
    )
    monkeypatch.setattr("app.routes.chat_sessions.route.ChatSessionCountController", lambda: count_controller)
    monkeypatch.setattr("app.routes.save_history.route.SaveHistoryController", lambda: save_controller)
    monkeypatch.setattr("app.routes.recent_history.route.RecentHistoryController", lambda: recent_controller)
    # No security overrides are installed. Restore any overrides if a test adds one.
    original_overrides = app.dependency_overrides.copy()
    yield app, authenticator, users, session, (
        count_controller, count_service, count_workflow, count_repository
    )
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


async def request_http(context, method, path, *, user_id=7, token=None, **kwargs):
    app, authenticator, *_ = context
    headers = {} if token == "missing" else {
        "Authorization": f"Bearer {token or authenticator.create_access_token(str(user_id))}"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await client.request(method, path, headers=headers, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("total", [0, 1, 12])
async def test_count_identity_layers_sql_and_response(history_http, total):
    _, _, users, session, layers = history_http
    result = Mock()
    result.scalar_one.return_value = total
    session.execute_result = result
    response = await request_http(history_http, "GET", "/api/v1/chat/sessions/count?user_id=99&id=99")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"] == {"total": total}
    assert response.headers["cache-control"] == "no-store"
    users.get_by_id.assert_awaited_once_with(7)
    for layer in layers[:3]:
        layer.execute.assert_awaited_once_with(user_id=7)
    layers[3].count_sessions_by_user_id.assert_awaited_once_with(user_id=7)
    statement = session.execute.await_args.args[0]
    expected = select(func.count(HistoryTable.id)).select_from(HistoryTable).where(
        HistoryTable.user_id == 7,
        HistoryTable.session_id.is_not(None),
        HistoryTable.status != HistoryStatus.DELETED,
    )
    assert statement.compare(expected)
    sql = str(statement.compile(dialect=postgresql.dialect())).upper()
    assert "LIMIT" not in sql
    assert "ACTIVE" not in sql and "ARCHIVED" not in sql


@pytest.mark.asyncio
async def test_count_database_error_is_500_and_not_zero(history_http):
    session = history_http[3]
    session.raises = "execute"
    response = await request_http(history_http, "GET", "/api/v1/chat/sessions/count")
    assert response.status_code == 500
    assert response.json()["success"] is False
    assert response.json()["data"] is None
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path", [
    ("GET", "/api/v1/chat/sessions/count"),
    ("POST", "/api/v1/save-history"),
    ("GET", "/api/v1/recent-history"),
])
@pytest.mark.parametrize("kind", ["missing", "invalid", "expired", "bad-signature", "unknown-user"])
async def test_real_authentication_rejects_requests(history_http, method, path, kind):
    authenticator = history_http[1]
    token = kind
    if kind in ("expired", "bad-signature"):
        token = jwt.encode({"sub": "7", "exp": datetime.now(timezone.utc) + timedelta(
            minutes=-1 if kind == "expired" else 10
        )}, authenticator.secret_key if kind == "expired" else "wrong-secret", algorithm="HS256")
    elif kind == "unknown-user":
        token = authenticator.create_access_token("99")
    response = await request_http(history_http, method, path, token=token,
                                  **({"json": {"title": "test", "message": {}}} if method == "POST" else {}))
    assert response.status_code == 401
    history_http[3].execute.assert_not_awaited()
    assert not hasattr(history_http[3], "instance")
    history_http[4][0].execute.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [7, 8])
async def test_save_uses_authenticated_owner_in_upsert(history_http, user_id):
    session = history_http[3]
    saved_id, session_id, dataset_id = uuid4(), "11111111-1111-1111-1111-111111111111", uuid4()
    session.execute_result = Result(saved_id)
    response = await request_http(history_http, "POST", "/api/v1/save-history?user_id=99", user_id=user_id,
        json={"user_id": 99, "session_id": session_id, "title": "updated", "message": {"text": "new"}, "dataset_id": str(dataset_id)})
    assert response.status_code == 200
    assert response.json()["data"]["history_id"] == str(saved_id)
    compiled = session.execute.await_args.args[0].compile(dialect=postgresql.dialect())
    assert compiled.params["user_id"] == user_id
    assert str(compiled.params["session_id"]) == session_id
    assert compiled.params["title"] == "updated"
    assert compiled.params["message"] == {"text": "new"}
    assert compiled.params["dataset_id"] == dataset_id
    assert "ON CONFLICT ON CONSTRAINT uq_history_user_session" in str(compiled)


@pytest.mark.asyncio
async def test_save_without_session_creates_independent_histories(history_http):
    ids = []
    for _ in range(2):
        response = await request_http(history_http, "POST", "/api/v1/save-history",
            json={"user_id": 99, "title": "legacy", "message": {}})
        assert response.status_code == 200
        ids.append(response.json()["data"]["history_id"])
        assert history_http[3].instance.user_id == 7
        assert history_http[3].instance.session_id is None
    assert ids[0] != ids[1]
    history_http[3].execute.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure,session_id,expected", [
    (None, True, 409), ("execute", True, 500), ("commit", True, 500),
    ("commit", False, 500), ("flush", False, 500),
])
async def test_save_failures_rollback_and_return_http_error(history_http, failure, session_id, expected):
    from sqlalchemy.exc import SQLAlchemyError
    session = history_http[3]
    session.raises = failure
    session.execute_result = Result(None if failure is None else uuid4())
    if failure == "flush":
        session.flush = AsyncMock(side_effect=SQLAlchemyError("flush failed"))
    payload = {"title": "test", "message": {}}
    if session_id:
        payload["session_id"] = str(uuid4())
    response = await request_http(history_http, "POST", "/api/v1/save-history", json=payload)
    assert response.status_code == expected
    assert response.json()["success"] is False
    assert response.json()["data"] == {"history_id": None}
    assert session.rolled_back
    assert not session.committed


@pytest.mark.asyncio
@pytest.mark.parametrize("fails", [False, True])
async def test_recent_empty_and_database_error_remain_distinct(history_http, fails):
    session = history_http[3]
    session.execute_result = Result([])
    session.raises = "execute" if fails else None
    response = await request_http(history_http, "GET", "/api/v1/recent-history?user_id=99")
    assert response.json()["success"] is (not fails)
    assert response.json()["data"] == []
    expected = select(HistoryTable).where(
        HistoryTable.user_id == 7, HistoryTable.status != HistoryStatus.DELETED
    ).order_by(HistoryTable.created_at.desc(), HistoryTable.id.desc()).limit(5)
    assert session.execute.await_args.args[0].compare(expected)


@pytest.mark.asyncio
async def test_recent_preserves_repository_order_and_active_archived(history_http):
    entries = [HistoryTable(
        id=uuid4(), user_id=7, title=title, status=status,
        created_at=datetime(2026, 1, day, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, day, tzinfo=timezone.utc),
    ) for title, status, day in [
        ("new", HistoryStatus.ARCHIVED, 2),
        ("old", HistoryStatus.ACTIVE, 1),
    ]]
    history_http[3].execute_result = Result(entries)
    response = await request_http(history_http, "GET", "/api/v1/recent-history")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert [item["id"] for item in response.json()["data"]] == [str(entry.id) for entry in entries]
    assert [item["status"] for item in response.json()["data"]] == ["ARCHIVED", "ACTIVE"]


@pytest.mark.asyncio
async def test_session_update_returns_existing_id_and_preserves_sql_fields(history_http):
    session = history_http[3]
    existing_id, session_id = uuid4(), uuid4()
    session.execute_result = Result(existing_id)
    for title in ("first", "updated"):
        response = await request_http(history_http, "POST", "/api/v1/save-history",
            json={"session_id": str(session_id), "title": title, "message": {"title": title}})
        assert response.status_code == 200
        assert response.json()["data"]["history_id"] == str(existing_id)
        compiled = session.execute.await_args.args[0].compile(dialect=postgresql.dialect())
        assignments = str(compiled).split("DO UPDATE SET ")[1].split(" WHERE")[0]
        assert {item.split(" = ")[0] for item in assignments.split(", ")} == {
            "title", "message", "dataset_id", "updated_at"
        }
        assert compiled.params["title"] == title
        assert compiled.params["message"] == {"title": title}
        assert "RETURNING history.id" in str(compiled)
