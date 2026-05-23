import pytest

from app.core.delete.user.workflow import DeleteUserWorkflow
from app.routes.delete.user.dtos.dto import DeleteUserRequestDTO


class DeletedUser:
    def __init__(self, user_id=1):
        self.id = user_id


class Repository:
    def __init__(self, deleted_user=None, raises=False):
        self.deleted_user = deleted_user
        self.raises = raises
        self.filters = None

    async def delete_user(self, filters):
        if self.raises:
            raise RuntimeError("boom")

        self.filters = filters
        return self.deleted_user


def create_request(
    user_id=None,
    email=None,
    cpf=None,
) -> DeleteUserRequestDTO:
    return DeleteUserRequestDTO(
        id=user_id,
        email=email,
        cpf=cpf,
    )


@pytest.mark.asyncio
async def test_run_deletes_user_by_id_successfully(fake_logger):
    repository = Repository(deleted_user=DeletedUser(user_id=8))
    workflow = DeleteUserWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_request(user_id=8))

    assert result == {
        "success": True,
        "message": "User deleted successfully.",
        "data": {
            "deleted_user_id": 8,
        },
    }

    assert repository.filters == {
        "id": 8,
    }


@pytest.mark.asyncio
async def test_run_deletes_user_by_email_successfully(fake_logger):
    repository = Repository(deleted_user=DeletedUser(user_id=9))
    workflow = DeleteUserWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_request(email="standard@example.com"))

    assert result == {
        "success": True,
        "message": "User deleted successfully.",
        "data": {
            "deleted_user_id": 9,
        },
    }

    assert repository.filters == {
        "email": "standard@example.com",
    }


@pytest.mark.asyncio
async def test_run_deletes_user_by_cpf_successfully(fake_logger):
    repository = Repository(deleted_user=DeletedUser(user_id=10))
    workflow = DeleteUserWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_request(cpf="12345678901"))

    assert result == {
        "success": True,
        "message": "User deleted successfully.",
        "data": {
            "deleted_user_id": 10,
        },
    }

    assert repository.filters == {
        "cpf": "12345678901",
    }


@pytest.mark.asyncio
async def test_run_builds_filters_with_all_fields(fake_logger):
    repository = Repository(deleted_user=DeletedUser(user_id=11))
    workflow = DeleteUserWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(
        create_request(
            user_id=11,
            email="standard@example.com",
            cpf="12345678901",
        )
    )

    assert result["success"] is True
    assert repository.filters == {
        "id": 11,
        "email": "standard@example.com",
        "cpf": "12345678901",
    }


@pytest.mark.asyncio
async def test_run_returns_failure_when_user_not_found(fake_logger):
    repository = Repository(deleted_user=None)
    workflow = DeleteUserWorkflow(
        repository=repository,
        logger=fake_logger,
    )

    result = await workflow.run(create_request(user_id=8))

    assert result == {
        "success": False,
        "message": "User not found or could not be deleted.",
        "data": None,
    }


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error(fake_logger):
    workflow = DeleteUserWorkflow(
        repository=Repository(raises=True),
        logger=fake_logger,
    )

    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run(create_request(user_id=8))
