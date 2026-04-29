from datetime import date

import pytest

from app.core.create.user.workflow import CreateUserWorkflow
from app.models.users_table import UserRole
from app.routes.create.user.dtos.dto import CreateUserRequestDTO


class Repository:
    def __init__(self, inserted_id=1, raises=False):
        self.inserted_id = inserted_id
        self.raises = raises
        self.instance = None

    async def insert(self, instance):
        if self.raises:
            raise RuntimeError("boom")
        self.instance = instance
        return self.inserted_id


class PasswordManager:
    def hash_password(self, password):
        return f"hashed-{password}"


def create_request() -> CreateUserRequestDTO:
    return CreateUserRequestDTO(
        name="Standard User",
        email="standard@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


@pytest.mark.asyncio
async def test_run_creates_standard_user(fake_logger):
    repository = Repository(inserted_id=8)
    workflow = CreateUserWorkflow(
        repository=repository,
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    result = await workflow.run(create_request())

    assert result == {
        "success": True,
        "message": "User created successfully.",
        "data": {"id": 8},
    }
    assert repository.instance.role == UserRole.USER
    assert repository.instance.password == "hashed-Strong@123"


@pytest.mark.asyncio
async def test_run_returns_failure_when_insert_fails(fake_logger):
    workflow = CreateUserWorkflow(
        repository=Repository(inserted_id=None),
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    result = await workflow.run(create_request())

    assert result["success"] is False
    assert result["message"] == "Failed to create user."


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error(fake_logger):
    workflow = CreateUserWorkflow(
        repository=Repository(raises=True),
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run(create_request())
