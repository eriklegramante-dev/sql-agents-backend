from app.models.users_table import UserRole, UserStatus, UserTable


def test_user_table_metadata_and_enums():
    assert UserTable.__tablename__ == "users"
    assert UserRole.ADMIN.value == "ADMIN"
    assert UserRole.USER.value == "USER"
    assert UserStatus.ACTIVE.value == "ACTIVE"
    assert UserStatus.INACTIVE.value == "INACTIVE"
