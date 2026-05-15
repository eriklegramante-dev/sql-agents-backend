from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from app.core.update.workflow import UpdateUserWorkflow
from app.models.users_table import UserRole, UserStatus
from app.routes.update.dtos.dto import UpdateUserRequestDTO


@pytest.mark.asyncio
async def test_should_return_error_when_user_not_found():
    repository = AsyncMock()
    repository.search_user_by_filters.return_value = None

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        name="Denilson",
    )

    result = await workflow.run(request)

    assert result["success"] is False
    assert result["message"] == "Target user not found."


@pytest.mark.asyncio
async def test_should_raise_validation_error_when_no_update_data():
    with pytest.raises(ValidationError):
        UpdateUserRequestDTO(id=1)


@pytest.mark.asyncio
async def test_should_update_email():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        email="test@example.com",
    )

    result = await workflow.run(request)

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={"email": "test@example.com"},
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_should_update_name():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        name="Denilson",
    )

    result = await workflow.run(request)

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={"name": "Denilson"},
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_should_update_role():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        role=UserRole.ADMIN,
    )

    result = await workflow.run(request)

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={"role": UserRole.ADMIN},
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_should_update_status():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        status=UserStatus.ACTIVE,
    )

    result = await workflow.run(request)

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={"status": UserStatus.ACTIVE},
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_should_hash_password_before_update():
    repository = AsyncMock()
    password_manager = Mock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    password_manager.hash_password.return_value = "hashed_password"

    workflow = UpdateUserWorkflow(
        repository=repository,
        password_manager=password_manager,
    )

    request = UpdateUserRequestDTO(
        id=1,
        password="Password123!",  # pragma: allowlist secret
    )

    result = await workflow.run(request)

    password_manager.hash_password.assert_called_once_with("Password123!")

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={"password": "hashed_password"},  # pragma: allowlist secret
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_should_return_error_when_update_fails():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = False

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        name="Denilson",
    )

    result = await workflow.run(request)

    assert result["success"] is False
    assert result["message"] == "Failed to update user."


@pytest.mark.asyncio
async def test_should_update_user_successfully():
    repository = AsyncMock()

    user = Mock(id=1)

    repository.search_user_by_filters.return_value = user
    repository.update_user.return_value = True

    workflow = UpdateUserWorkflow(repository=repository)

    request = UpdateUserRequestDTO(
        id=1,
        name="Denilson",
        email="denilson@example.com",
    )

    result = await workflow.run(request)

    repository.update_user.assert_called_once_with(
        user=user,
        update_data={
            "email": "denilson@example.com",
            "name": "Denilson",
        },
    )

    assert result["success"] is True
    assert result["message"] == "User updated successfully."
    assert result["data"] == {"id": 1}
