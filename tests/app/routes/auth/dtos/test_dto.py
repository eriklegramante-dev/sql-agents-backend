import pytest
from pydantic import ValidationError

from app.routes.auth.dtos.dto import LoginRequestDTO, LoginResponseDTO


def test_login_request_accepts_valid_payload():
    dto = LoginRequestDTO(username="user@example.com", password="Strong@123")

    assert dto.username == "user@example.com"


def test_login_request_rejects_password_with_space():
    with pytest.raises(ValidationError):
        LoginRequestDTO(username="user@example.com", password="Strong @123")


def test_login_response_serializes_payload():
    dto = LoginResponseDTO(
        success=True,
        message="ok",
        access_token="token",
        token_type="bearer",
    )

    assert dto.model_dump() == {
        "success": True,
        "message": "ok",
        "access_token": "token",
        "token_type": "bearer",
    }
