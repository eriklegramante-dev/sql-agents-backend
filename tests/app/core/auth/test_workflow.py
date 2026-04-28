from types import SimpleNamespace

import pytest

from app.core.auth.workflow import LoginWorkflow
from app.routes.auth.dtos.dto import LoginRequestDTO


class Repository:
    def __init__(self, user=None, updated=True, raises=False):
        self.user = user
        self.updated = updated
        self.raises = raises

    async def get_user_by_email(self, email):
        if self.raises:
            raise RuntimeError("boom")
        return self.user

    async def update_last_login_at(self, user_id):
        return self.updated


class PasswordManager:
    def __init__(self, valid=True):
        self.valid = valid

    def verify_password(self, plain_password, hashed_password):
        return self.valid


class Authenticator:
    def create_access_token(self, subject):
        return f"token-{subject}"


def login_request() -> LoginRequestDTO:
    return LoginRequestDTO(username="user@example.com", password="Strong@123")


@pytest.mark.asyncio
async def test_run_returns_token_for_valid_credentials(fake_logger):
    user = SimpleNamespace(id=7, password="hash")
    workflow = LoginWorkflow(
        repository=Repository(user=user),
        logger=fake_logger,
        authenticator=Authenticator(),
        password_manager=PasswordManager(valid=True),
    )

    result = await workflow.run(login_request())

    assert result["success"] is True
    assert result["access_token"] == "token-7"


@pytest.mark.asyncio
async def test_run_returns_success_when_last_login_update_fails(fake_logger):
    user = SimpleNamespace(id=7, password="hash")
    workflow = LoginWorkflow(
        repository=Repository(user=user, updated=False),
        logger=fake_logger,
        authenticator=Authenticator(),
        password_manager=PasswordManager(valid=True),
    )

    result = await workflow.run(login_request())

    assert result["success"] is True


@pytest.mark.asyncio
async def test_run_rejects_missing_user(fake_logger):
    workflow = LoginWorkflow(
        repository=Repository(user=None),
        logger=fake_logger,
        authenticator=Authenticator(),
        password_manager=PasswordManager(valid=True),
    )

    result = await workflow.run(login_request())

    assert result["success"] is False
    assert result["message"] == "Invalid credentials."


@pytest.mark.asyncio
async def test_run_rejects_invalid_password(fake_logger):
    user = SimpleNamespace(id=7, password="hash")
    workflow = LoginWorkflow(
        repository=Repository(user=user),
        logger=fake_logger,
        authenticator=Authenticator(),
        password_manager=PasswordManager(valid=False),
    )

    result = await workflow.run(login_request())

    assert result["success"] is False
    assert result["message"] == "Invalid credentials."


@pytest.mark.asyncio
async def test_run_propagates_unexpected_error(fake_logger):
    workflow = LoginWorkflow(
        repository=Repository(raises=True),
        logger=fake_logger,
        authenticator=Authenticator(),
        password_manager=PasswordManager(valid=True),
    )

    with pytest.raises(RuntimeError, match="boom"):
        await workflow.run(login_request())
