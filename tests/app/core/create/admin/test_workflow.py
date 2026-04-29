from datetime import date

import pytest

from app.core.create.admin.workflow import CreateAdminWorkflow
from app.models.users_table import UserRole
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO


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


def create_request() -> CreateAdminRequestDTO:
    return CreateAdminRequestDTO(
        name="Admin User",
        email="admin@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


@pytest.mark.asyncio
async def test_run_creates_admin_user(fake_logger):
    repository = Repository(inserted_id=8)
    workflow = CreateAdminWorkflow(
        repository=repository,
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    result = await workflow.run(create_request())

    assert result == {
        "success": True,
        "message": "Admin user created successfully.",
        "data": {"id": 8},
    }
    assert repository.instance.role == UserRole.ADMIN
    assert repository.instance.password == "hashed-Strong@123"


@pytest.mark.asyncio
async def test_run_returns_failure_when_insert_fails(fake_logger):
    workflow = CreateAdminWorkflow(
        repository=Repository(inserted_id=None),
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    result = await workflow.run(create_request())

    assert result["success"] is False
    assert result["message"] == "Failed to create admin user."


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error(fake_logger):
    workflow = CreateAdminWorkflow(
        repository=Repository(raises=True),
        logger=fake_logger,
        password_manager=PasswordManager(),
    )

    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run(create_request())
