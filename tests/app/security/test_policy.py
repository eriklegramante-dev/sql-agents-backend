from datetime import date

from app.models.users_table import UserRole, UserTable
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.security.policy import UserPolicy


def user(role: UserRole) -> UserTable:
    return UserTable(id=1, role=role)


def user_request() -> CreateUserRequestDTO:
    return CreateUserRequestDTO(
        name="Standard User",
        email="standard@example.com",
        cpf="12345678901",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


def admin_request() -> CreateAdminRequestDTO:
    return CreateAdminRequestDTO(
        name="Admin User",
        email="admin@example.com",
        cpf="12345678902",
        birth_date=date(1990, 1, 1),
        country="Brazil",
        password="Strong@123",
    )


def test_can_create_allows_admin_for_standard_user_request(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    assert policy.can_create(user_request(), user(UserRole.ADMIN)) is True


def test_can_create_allows_admin_for_admin_request(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    assert policy.can_create(admin_request(), user(UserRole.ADMIN)) is True


def test_can_create_denies_standard_user(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    assert policy.can_create(user_request(), user(UserRole.USER)) is False


def test_future_policy_methods_return_none(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    assert policy.can_view(object(), user(UserRole.USER)) is None
    assert policy.can_update(object(), user(UserRole.USER)) is None
    assert policy.can_delete(object(), user(UserRole.USER)) is None
