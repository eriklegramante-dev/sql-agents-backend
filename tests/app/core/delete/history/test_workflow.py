import pytest

from app.core.delete.history.workflow import DeleteHistoryWorkflow
from app.models.users_table import UserTable


class DeletedHistory:
    def __init__(self, history_id=1):
        self.id = history_id


class Repository:
    def __init__(self, deleted_history=None, raises=False):
        self.deleted_history = deleted_history
        self.raises = raises
        self.user_id = None

    async def delete_oldest_chat_history_by_user_id(self, user_id):
        if self.raises:
            raise RuntimeError("boom")

        self.user_id = user_id
        return self.deleted_history


def create_current_user(user_id=1):
    user = UserTable()
    user.id = user_id
    return user


@pytest.mark.asyncio
async def test_run_deletes_oldest_history_successfully(fake_logger):
    repository = Repository(deleted_history=DeletedHistory(history_id=8))
    workflow = DeleteHistoryWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_current_user(user_id=1))

    assert result == {
        "success": True,
        "message": "Chat history deleted successfully.",
        "data": {
            "deleted_history_id": 8,
        },
    }

    assert repository.user_id == 1


@pytest.mark.asyncio
async def test_run_returns_failure_when_history_not_found(fake_logger):
    repository = Repository(deleted_history=None)
    workflow = DeleteHistoryWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_current_user(user_id=1))

    assert result == {
        "success": False,
        "message": "Chat history not found or could not be deleted.",
        "data": None,
    }

    assert repository.user_id == 1


@pytest.mark.asyncio
async def test_run_uses_authenticated_user_id(fake_logger):
    repository = Repository(deleted_history=DeletedHistory(history_id=10))
    workflow = DeleteHistoryWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_current_user(user_id=77))

    assert result["success"] is True
    assert result["data"]["deleted_history_id"] == 10
    assert repository.user_id == 77


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error(fake_logger):
    workflow = DeleteHistoryWorkflow(
        repository=Repository(raises=True),
        logger=fake_logger,
    )

    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run(create_current_user(user_id=1))
