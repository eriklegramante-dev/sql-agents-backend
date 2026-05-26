from unittest.mock import AsyncMock, Mock

import pytest

from app.core.read.workflow import ReadUserWorkflow
from app.models.users_table import UserRole


@pytest.mark.asyncio
async def test_should_return_error_when_no_users_found():

    repository = AsyncMock()

    repository.read_user.return_value = []

    workflow = ReadUserWorkflow(
        repository=repository
    )

    request = Mock()

    request.id = None
    request.email = None
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()
    current_user.role = UserRole.ADMIN

    result = await workflow.run(
        request=request,
        current_user=current_user,
    )

    assert result["success"] is False
    assert result["message"] == "No users found"


@pytest.mark.asyncio
async def test_should_return_users_successfully():

    repository = AsyncMock()

    user = Mock()

    user.id = 1
    user.name = "Ronald"
    user.email = "ronald@test.com"
    user.country = "Brazil"

    user.role.value = "USER"
    user.status.value = "ACTIVE"

    repository.read_user.return_value = [user]

    workflow = ReadUserWorkflow(
        repository=repository
    )

    request = Mock()

    request.id = None
    request.email = None
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()
    current_user.role = UserRole.ADMIN

    result = await workflow.run(
        request=request,
        current_user=current_user,
    )

    assert result["success"] is True
    assert result["message"] == "Users found successfully"

    assert result["data"] == [
        {
            "id": 1,
            "name": "Ronald",
            "email": "ronald@test.com",
            "country": "Brazil",
            "role": "USER",
            "status": "ACTIVE",
        }
    ]


@pytest.mark.asyncio
async def test_should_force_common_user_to_view_own_profile():

    repository = AsyncMock()

    repository.read_user.return_value = []

    workflow = ReadUserWorkflow(
        repository=repository
    )

    request = Mock()

    request.id = None
    request.email = None
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()

    current_user.id = 10
    current_user.role = UserRole.USER

    await workflow.run(
        request=request,
        current_user=current_user,
    )

    repository.read_user.assert_called_once_with(
        {"id": 10}
    )


@pytest.mark.asyncio
async def test_should_apply_all_filters():

    repository = AsyncMock()

    repository.read_user.return_value = []

    workflow = ReadUserWorkflow(
        repository=repository
    )

    request = Mock()

    request.id = 1
    request.email = "user@test.com"
    request.name = "Ronald"
    request.cpf = "12345678900"
    request.country = "Brazil"
    request.role = "USER"
    request.status = "ACTIVE"

    current_user = Mock()
    current_user.role = UserRole.ADMIN

    await workflow.run(
        request=request,
        current_user=current_user,
    )

    repository.read_user.assert_called_once_with(
        {
            "id": 1,
            "email": "user@test.com",
            "name": "Ronald",
            "cpf": "12345678900",
            "country": "Brazil",
            "role": "USER",
            "status": "ACTIVE",
        }
    )