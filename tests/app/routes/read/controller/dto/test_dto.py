import pytest

from pydantic import ValidationError

from app.routes.read.dtos.dto import (
    GetUserRequestDTO,
    GetUserResponseDTO,
)


def test_should_accept_valid_cpf():

    dto = GetUserRequestDTO(
        cpf="123.456.789-00"
    )

    assert dto.cpf == "12345678900"


def test_should_reject_invalid_cpf():

    with pytest.raises(ValidationError):

        GetUserRequestDTO(
            cpf="abc"
        )


def test_should_reject_invalid_cpf_size():

    with pytest.raises(ValidationError):

        GetUserRequestDTO(
            cpf="123"
        )


def test_should_serialize_response():

    dto = GetUserResponseDTO(
        success=True,
        message="success",
        data={"id": 1},
    )

    assert dto.model_dump() == {
        "success": True,
        "message": "success",
        "data": {"id": 1},
    }