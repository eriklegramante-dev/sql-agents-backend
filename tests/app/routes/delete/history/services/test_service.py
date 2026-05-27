import pytest

from app.models.users_table import UserTable
from app.routes.delete.history.services.service import DeleteHistoryService


class FakeLogger:
    def __init__(self):
        self.infos = []
        self.debugs = []

    def log_info(self, message):
        self.infos.append(message)

    def log_debug(self, message):
        self.debugs.append(message)


class FakeWorkflow:
    def __init__(self, result):
        self.result = result
        self.called_with = None

    async def run(self, current_user):
        self.called_with = current_user
        return self.result


def create_current_user(user_id=1):
    user = UserTable()
    user.id = user_id
    return user


@pytest.mark.asyncio
async def test_handle_delete_success_with_deleted_history_id():
    current_user = create_current_user(user_id=1)

    workflow = FakeWorkflow(
        {
            "success": True,
            "message": "Chat history deleted successfully.",
            "data": {"deleted_history_id": 1},
        }
    )
    logger = FakeLogger()

    service = DeleteHistoryService(workflow=workflow, logger=logger)

    response = await service.handle_delete(current_user)

    assert response.success is True
    assert response.message == "Chat history deleted successfully."
    assert response.data["deleted_history_id"] == 1
    assert workflow.called_with == current_user
    assert logger.infos == ["[service] processing delete history request"]
    assert len(logger.debugs) == 2


@pytest.mark.asyncio
async def test_handle_delete_failure_without_data():
    current_user = create_current_user(user_id=1)

    workflow = FakeWorkflow(
        {
            "success": False,
            "message": "Chat history not found.",
        }
    )
    logger = FakeLogger()

    service = DeleteHistoryService(workflow=workflow, logger=logger)

    response = await service.handle_delete(current_user)

    assert response.success is False
    assert response.message == "Chat history not found."
    assert response.data is None
    assert workflow.called_with == current_user
    assert len(logger.debugs) == 2


@pytest.mark.asyncio
async def test_handle_delete_success_with_empty_data():
    current_user = create_current_user(user_id=1)

    workflow = FakeWorkflow(
        {
            "success": True,
            "message": "Chat history deleted.",
            "data": {},
        }
    )
    logger = FakeLogger()

    service = DeleteHistoryService(workflow=workflow, logger=logger)

    response = await service.handle_delete(current_user)

    assert response.success is True
    assert response.message == "Chat history deleted."
    assert response.data == {}


@pytest.mark.asyncio
async def test_handle_delete_default_success_false_when_missing_success():
    current_user = create_current_user(user_id=99)

    workflow = FakeWorkflow(
        {
            "message": "Unexpected response.",
            "data": {"deleted_history_id": 99},
        }
    )
    logger = FakeLogger()

    service = DeleteHistoryService(workflow=workflow, logger=logger)

    response = await service.handle_delete(current_user)

    assert response.success is False
    assert response.message == "Unexpected response."
    assert response.data["deleted_history_id"] == 99


@pytest.mark.asyncio
async def test_handle_delete_message_none_when_missing_message():
    current_user = create_current_user(user_id=10)

    workflow = FakeWorkflow(
        {
            "success": True,
            "data": {"deleted_history_id": 10},
        }
    )
    logger = FakeLogger()

    service = DeleteHistoryService(workflow=workflow, logger=logger)

    response = await service.handle_delete(current_user)

    assert response.success is True
    assert response.message is None
    assert response.data["deleted_history_id"] == 10


@pytest.mark.asyncio
async def test_handle_delete_using_monkeypatch_default_dependencies(monkeypatch):
    current_user = create_current_user(user_id=7)

    fake_workflow = FakeWorkflow(
        {
            "success": True,
            "message": "Deleted with monkeypatch.",
            "data": {"deleted_history_id": 7},
        }
    )

    fake_logger = FakeLogger()

    monkeypatch.setattr(
        "app.routes.delete.history.services.service.DeleteHistoryWorkflow",
        lambda: fake_workflow,
    )

    monkeypatch.setattr(
        "app.routes.delete.history.services.service.LOGGER",
        fake_logger,
    )

    service = DeleteHistoryService()

    response = await service.handle_delete(current_user)

    assert response.success is True
    assert response.message == "Deleted with monkeypatch."
    assert response.data["deleted_history_id"] == 7
    assert fake_workflow.called_with == current_user
    assert len(fake_logger.infos) == 1
    assert len(fake_logger.debugs) == 2
