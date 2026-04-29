from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.routes.create.admin.dtos.dto import (
    CreateAdminRequestDTO,
    CreateAdminResponseDTO,
)


def valid_payload() -> dict:
    return {
        "name": "Admin User",
        "email": "admin@example.com",
        "cpf": "12345678901",
        "birth_date": date(1990, 1, 1),
        "country": "Brazil",
        "password": "Strong@123",
    }


def test_create_admin_request_accepts_valid_payload():
    dto = CreateAdminRequestDTO(**valid_payload())

    assert dto.email == "admin@example.com"
    assert dto.cpf == "12345678901"


@pytest.mark.parametrize(
    "field,value",
    [
        ("cpf", "1234567890a"),
        ("name", "Admin 123"),
        ("birth_date", date.today() + timedelta(days=1)),
        ("birth_date", date(date.today().year - 121, 1, 1)),
        ("country", "   "),
        ("country", "Brazil123"),
        ("password", "strong@123"),
        ("password", "STRONG@123"),
        ("password", "StrongPass"),
        ("password", "Strong123"),
        ("password", "Strong @123"),
    ],
)
def test_create_admin_request_rejects_invalid_fields(field, value):
    payload = valid_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        CreateAdminRequestDTO(**payload)


def test_create_admin_response_serializes_payload():
    dto = CreateAdminResponseDTO(success=True, message="ok", data={"id": 1})

    assert dto.model_dump() == {"success": True, "message": "ok", "data": {"id": 1}}
