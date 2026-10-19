"""Counting composes real layers around a structural repository contract."""

from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.chat_sessions.contracts import ChatSessionCountRepository
from app.core.chat_sessions.workflow import ChatSessionCountWorkflow
from app.models.history_table import HistoryTable
from app.routes.chat_sessions.controllers.controller import ChatSessionCountController
from app.routes.chat_sessions.dependencies import dependencie as dependencies
from app.routes.chat_sessions.services.service import ChatSessionCountService
from tests.conftest import response_content


class FakeCountRepository:
    def __init__(self, total=0, error=None):
        self.total = total
        self.error = error
        self.user_ids = []

    async def count_sessions_by_user_id(self, user_id: int) -> int:
        self.user_ids.append(user_id)
        if self.error is not None:
            raise self.error
        return self.total


@pytest.mark.asyncio
@pytest.mark.parametrize("total", [0, 1, 12])
async def test_workflow_accepts_repository_contract(total):
    fake = FakeCountRepository(total=total)
    repository: ChatSessionCountRepository = fake
    workflow = ChatSessionCountWorkflow(repository=repository)

    assert await workflow.execute(user_id=8) == total
    assert fake.user_ids == [8]


@pytest.mark.asyncio
async def test_workflow_propagates_repository_failure():
    error = SQLAlchemyError("count failed")
    fake = FakeCountRepository(error=error)
    workflow = ChatSessionCountWorkflow(repository=fake)

    with pytest.raises(SQLAlchemyError) as raised:
        await workflow.execute(user_id=7)

    assert raised.value is error
    assert fake.user_ids == [7]


@pytest.mark.asyncio
@pytest.mark.parametrize("total", [0, 1, 12])
async def test_composition_uses_injected_repository(monkeypatch, fake_logger, total):
    fake = FakeCountRepository(total=total)
    factory = Mock(return_value=fake)
    monkeypatch.setattr(dependencies, "HistorySessionRepository", factory)

    controller = dependencies.get_chat_session_count_controller()
    controller.logger = fake_logger

    factory.assert_called_once_with(model=HistoryTable)
    assert isinstance(controller, ChatSessionCountController)
    assert isinstance(controller.service, ChatSessionCountService)
    assert isinstance(controller.service.workflow, ChatSessionCountWorkflow)
    assert controller.service.workflow.repository is fake
    response = await controller.execute(user_id=8)
    assert response.status_code == 200
    assert response_content(response)["data"] == {"total": total}
    assert response_content(response)["success"] is True
    assert response.headers["cache-control"] == "no-store"
    assert fake.user_ids == [8]


@pytest.mark.asyncio
async def test_composed_database_failure_is_not_a_zero_count(monkeypatch, fake_logger):
    fake = FakeCountRepository(error=SQLAlchemyError("count failed"))
    monkeypatch.setattr(dependencies, "HistorySessionRepository", Mock(return_value=fake))
    controller = dependencies.get_chat_session_count_controller()
    controller.logger = fake_logger

    response = await controller.execute(user_id=7)

    assert response.status_code == 500
    assert response_content(response)["success"] is False
    assert response_content(response)["data"] is None
    assert response.headers["cache-control"] == "no-store"
    assert fake.user_ids == [7]
