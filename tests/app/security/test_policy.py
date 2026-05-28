from datetime import date


from app.models.users_table import UserRole, UserTable
from app.routes.create.admin.dtos.dto import CreateAdminRequestDTO
from app.routes.create.user.dtos.dto import CreateUserRequestDTO
from app.security.policy import UserPolicy
from app.routes.delete.user.dtos.dto import DeleteUserRequestDTO

from unittest.mock import Mock


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


def test_can_view_allows_admin(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = Mock()

    current_user = Mock()

    current_user.id = 1
    current_user.role = UserRole.ADMIN

    assert (
        policy.can_view(
            request=request,
            current_user=current_user,
        )
        is True
    )


def test_can_view_allows_user_own_profile(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = Mock()

    request.id = 10
    request.email = None
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()

    current_user.id = 10
    current_user.role = UserRole.USER

    assert (
        policy.can_view(
            request=request,
            current_user=current_user,
        )
        is True
    )


def test_can_view_denies_user_from_other_profile(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = Mock()

    request.id = 20
    request.email = None
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()

    current_user.id = 10
    current_user.role = UserRole.USER

    assert (
        policy.can_view(
            request=request,
            current_user=current_user,
        )
        is False
    )


def test_can_view_denies_forbidden_filters(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = Mock()

    request.id = None
    request.email = "test@test.com"
    request.name = None
    request.cpf = None
    request.country = None
    request.role = None
    request.status = None

    current_user = Mock()

    current_user.id = 10
    current_user.role = UserRole.USER

    assert (
        policy.can_view(
            request=request,
            current_user=current_user,
        )
        is False
    )


def test_can_update_denies_user_updating_other_profile(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    class FakeRequest:
        id = 2
        role = None
        status = None

    assert (
        policy.can_update(
            FakeRequest(),
            user(UserRole.USER),
        )
        is False
    )


def test_can_update_denies_role_change(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    class FakeRequest:
        id = 1
        role = UserRole.ADMIN
        status = None

    assert (
        policy.can_update(
            FakeRequest(),
            user(UserRole.USER),
        )
        is False
    )


def test_can_update_denies_status_change(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    class FakeRequest:
        id = 1
        role = None
        status = "ACTIVE"

    assert (
        policy.can_update(
            FakeRequest(),
            user(UserRole.USER),
        )
        is False
    )


def delete_user(
    role: UserRole = UserRole.USER,
    user_id: int = 1,
    email: str = "user@example.com",
    cpf: str = "12345678901",
) -> UserTable:
    return UserTable(
        id=user_id,
        role=role,
        email=email,
        cpf=cpf,
    )


def test_can_delete_allows_admin(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(id=999)

    current_user = delete_user(
        role=UserRole.ADMIN,
        user_id=1,
        email="admin@example.com",
        cpf="12345678901",
    )

    assert policy.can_delete(request, current_user) is True


def test_can_delete_allows_user_by_own_id(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(id=1)

    current_user = delete_user(user_id=1)

    assert policy.can_delete(request, current_user) is True


def test_can_delete_allows_user_by_own_email(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(email="user@example.com")

    current_user = delete_user(email="user@example.com")

    assert policy.can_delete(request, current_user) is True


def test_can_delete_allows_user_by_own_cpf(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(cpf="12345678901")

    current_user = delete_user(cpf="12345678901")

    assert policy.can_delete(request, current_user) is True


def test_can_delete_denies_user_with_different_id(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(id=2)

    current_user = delete_user(user_id=1)

    assert policy.can_delete(request, current_user) is False


def test_can_delete_denies_user_with_different_email(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(email="other@example.com")

    current_user = delete_user(email="user@example.com")

    assert policy.can_delete(request, current_user) is False


def test_can_delete_denies_user_with_different_cpf(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO(cpf="99999999999")

    current_user = delete_user(cpf="12345678901")

    assert policy.can_delete(request, current_user) is False


def test_can_delete_denies_user_without_identifier(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    request = DeleteUserRequestDTO()

    current_user = delete_user()

    assert policy.can_delete(request, current_user) is False


def test_policy_uses_default_logger_with_monkeypatch(monkeypatch, fake_logger):
    monkeypatch.setattr("app.security.policy.LOGGER", fake_logger)

    policy = UserPolicy()

    assert policy.logger is fake_logger


def test_can_update_allows_user_to_update_own_profile(fake_logger):
    policy = UserPolicy(logger=fake_logger)

    class FakeRequest:
        id = 1
        role = None
        status = None

    assert policy.can_update(FakeRequest(), user(UserRole.USER)) is True
