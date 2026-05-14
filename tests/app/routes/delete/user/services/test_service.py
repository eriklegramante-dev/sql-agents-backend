import pytest

from app.routes.delete.user.dtos.dto import DeleteUserRequestDTO
from app.routes.delete.user.services.service import DeleteUserService


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

    async def run(self, request):
        self.called_with = request
        return self.result


@pytest.mark.asyncio
async def test_handle_delete_success_with_deleted_user_id():
    request = DeleteUserRequestDTO(id=1)

    workflow = FakeWorkflow(
        {
            "success": True,
            "message": "User deleted successfully.",
            "data": {"deleted_user_id": 1},
        }
    )
    logger = FakeLogger()

    service = DeleteUserService(workflow=workflow, logger=logger)

    response = await service.handle_delete(request)

    assert response.success is True
    assert response.message == "User deleted successfully."
    assert response.deleted_user_id == 1
    assert workflow.called_with == request

    assert logger.infos == ["[service] processing delete user request"]
    assert len(logger.debugs) == 2


@pytest.mark.asyncio
async def test_handle_delete_failure_without_data():
    request = DeleteUserRequestDTO(email="user@example.com")

    workflow = FakeWorkflow(
        {
            "success": False,
            "message": "User not found.",
        }
    )
    logger = FakeLogger()

    service = DeleteUserService(workflow=workflow, logger=logger)

    response = await service.handle_delete(request)

    assert response.success is False
    assert response.message == "User not found."
    assert response.deleted_user_id is None
    assert workflow.called_with == request
    assert len(logger.debugs) == 2


@pytest.mark.asyncio
async def test_handle_delete_success_with_empty_data():
    request = DeleteUserRequestDTO(cpf="12345678901")

    workflow = FakeWorkflow(
        {
            "success": True,
            "message": "User deleted.",
            "data": {},
        }
    )
    logger = FakeLogger()

    service = DeleteUserService(workflow=workflow, logger=logger)

    response = await service.handle_delete(request)

    assert response.success is True
    assert response.message == "User deleted."
    assert response.deleted_user_id is None


@pytest.mark.asyncio
async def test_handle_delete_default_success_false_when_missing_success():
    request = DeleteUserRequestDTO(id=99)

    workflow = FakeWorkflow(
        {
            "message": "Unexpected response.",
            "data": {"deleted_user_id": 99},
        }
    )
    logger = FakeLogger()

    service = DeleteUserService(workflow=workflow, logger=logger)

    response = await service.handle_delete(request)

    assert response.success is False
    assert response.message == "Unexpected response."
    assert response.deleted_user_id == 99


@pytest.mark.asyncio
async def test_handle_delete_message_none_when_missing_message():
    request = DeleteUserRequestDTO(id=10)

    workflow = FakeWorkflow(
        {
            "success": True,
            "data": {"deleted_user_id": 10},
        }
    )
    logger = FakeLogger()

    service = DeleteUserService(workflow=workflow, logger=logger)

    response = await service.handle_delete(request)

    assert response.success is True
    assert response.message is None
    assert response.deleted_user_id == 10


@pytest.mark.asyncio
async def test_handle_delete_using_monkeypatch_default_dependencies(monkeypatch):
    request = DeleteUserRequestDTO(id=7)

    fake_workflow = FakeWorkflow(
        {
            "success": True,
            "message": "Deleted with monkeypatch.",
            "data": {"deleted_user_id": 7},
        }
    )

    fake_logger = FakeLogger()

    monkeypatch.setattr(
        "app.routes.delete.user.services.service.DeleteUserWorkflow",
        lambda: fake_workflow,
    )

    monkeypatch.setattr(
        "app.routes.delete.user.services.service.LOGGER",
        fake_logger,
    )

    service = DeleteUserService()

    response = await service.handle_delete(request)

    assert response.success is True
    assert response.message == "Deleted with monkeypatch."
    assert response.deleted_user_id == 7
    assert fake_workflow.called_with == request
    assert len(fake_logger.infos) == 1
    assert len(fake_logger.debugs) == 2