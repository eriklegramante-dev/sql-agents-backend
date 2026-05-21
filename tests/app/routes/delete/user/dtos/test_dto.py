import pytest
from pydantic import ValidationError

from app.routes.delete.user.dtos.dto import (
    DeleteUserRequestDTO,
    DeleteUserResponseDTO,
)


def test_delete_user_request_accepts_id():
    dto = DeleteUserRequestDTO(id=1)

    assert dto.id == 1
    assert dto.email is None
    assert dto.cpf is None


def test_delete_user_request_accepts_email():
    dto = DeleteUserRequestDTO(email="user@example.com")

    assert dto.email == "user@example.com"
    assert dto.id is None
    assert dto.cpf is None


def test_delete_user_request_accepts_valid_cpf():
    dto = DeleteUserRequestDTO(cpf="12345678901")

    assert dto.cpf == "12345678901"


def test_delete_user_request_accepts_all_fields():
    dto = DeleteUserRequestDTO(
        id=1,
        email="user@example.com",
        cpf="12345678901",
    )

    assert dto.id == 1
    assert dto.email == "user@example.com"
    assert dto.cpf == "12345678901"


def test_delete_user_request_accepts_empty_request():
    dto = DeleteUserRequestDTO()

    assert dto.id is None
    assert dto.email is None
    assert dto.cpf is None


def test_delete_user_request_rejects_invalid_email():
    with pytest.raises(ValidationError):
        DeleteUserRequestDTO(email="invalid-email")


def test_delete_user_request_rejects_cpf_with_letters():
    with pytest.raises(ValidationError) as error:
        DeleteUserRequestDTO(cpf="1234567890a")

    assert "CPF must contain only digits." in str(error.value)


def test_delete_user_request_rejects_cpf_shorter_than_11_digits():
    with pytest.raises(ValidationError):
        DeleteUserRequestDTO(cpf="1234567890")


def test_delete_user_request_rejects_cpf_longer_than_11_digits():
    with pytest.raises(ValidationError):
        DeleteUserRequestDTO(cpf="123456789012")


def test_delete_user_response_success_with_deleted_user_id():
    dto = DeleteUserResponseDTO(
        success=True,
        message="User deleted successfully.",
        data={"deleted_user_id": 1},
    )

    assert dto.success is True
    assert dto.message == "User deleted successfully."
    assert dto.data["deleted_user_id"] == 1


def test_delete_user_response_failure_without_deleted_user_id():
    dto = DeleteUserResponseDTO(
        success=False,
        message="User not found.",
    )

    assert dto.success is False
    assert dto.message == "User not found."
    assert dto.data is None


def test_delete_user_response_accepts_empty_data_dict():
    dto = DeleteUserResponseDTO(
        success=True,
        message="User deleted successfully.",
        data={},
    )

    assert dto.success is True
    assert dto.message == "User deleted successfully."
    assert dto.data == {}


def test_delete_user_response_requires_success():
    with pytest.raises(ValidationError):
        DeleteUserResponseDTO()
