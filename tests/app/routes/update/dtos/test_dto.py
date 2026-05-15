import pytest
from pydantic import ValidationError

from app.models.users_table import UserRole, UserStatus
from app.routes.update.dtos.dto import UpdateUserRequestDTO, UpdateUserResponseDTO


def valid_payload() -> dict:
    return {
        "id": 1,
        "email": "user@example.com",
        "name": "Updated User",
        "password": "Strong@123",  # pragma: allowlist secret
    }


def test_update_user_request_accepts_valid_payload():
    dto = UpdateUserRequestDTO(**valid_payload())

    assert dto.id == 1
    assert dto.email == "user@example.com"
    assert dto.name == "Updated User"


@pytest.mark.parametrize(
    "field,value",
    [
        ("email", "bad-email"),
        ("name", "User 123"),
        ("password", "strong@123"),
        ("password", "STRONG@123"),
        ("password", "StrongPass"),
        ("password", "Strong123"),  # pragma: allowlist secret
        ("password", "Strong @123"),  # pragma: allowlist secret
    ],
)
def test_update_user_request_rejects_invalid_fields(field, value):
    payload = valid_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        UpdateUserRequestDTO(**payload)


def test_update_user_request_accepts_role_and_status_enums():
    dto = UpdateUserRequestDTO(
        id=1,
        name="Updated User",
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
    )

    assert dto.role == UserRole.USER
    assert dto.status == UserStatus.ACTIVE


def test_update_user_response_serializes_payload():
    dto = UpdateUserResponseDTO(success=True, message="ok", data={"id": 1})

    assert dto.model_dump() == {"success": True, "message": "ok", "data": {"id": 1}}
