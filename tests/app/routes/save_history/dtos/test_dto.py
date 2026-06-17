from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.routes.save_history.dtos.dto import (
    SaveHistoryRequestDTO,
    SaveHistoryResponseDTO,
    SaveHistoryResponseDataDTO,
)


def test_should_create_request_dto_with_all_fields():
    dataset_id = uuid4()

    dto = SaveHistoryRequestDTO(
        title="History Title",
        message={
            "role": "user",
            "content": "Hello",
        },
        dataset_id=dataset_id,
    )

    assert dto.title == "History Title"
    assert dto.message == {
        "role": "user",
        "content": "Hello",
    }
    assert dto.dataset_id == dataset_id


def test_should_create_request_dto_without_dataset_id():
    dto = SaveHistoryRequestDTO(
        title="History Title",
        message={
            "role": "user",
            "content": "Hello",
        },
    )

    assert dto.dataset_id is None


def test_should_reject_empty_title():
    with pytest.raises(ValidationError):
        SaveHistoryRequestDTO(
            title="",
            message={
                "role": "user",
                "content": "Hello",
            },
        )


def test_should_create_response_data_dto():
    history_id = uuid4()

    dto = SaveHistoryResponseDataDTO(
        history_id=history_id,
    )

    assert dto.history_id == history_id


def test_should_create_response_dto():
    history_id = uuid4()

    dto = SaveHistoryResponseDTO(
        success=True,
        message="History saved successfully.",
        data=SaveHistoryResponseDataDTO(
            history_id=history_id,
        ),
    )

    assert dto.success is True
    assert dto.message == "History saved successfully."
    assert dto.data.history_id == history_id


def test_should_serialize_response_dto():
    history_id = uuid4()

    dto = SaveHistoryResponseDTO(
        success=True,
        message="History saved successfully.",
        data=SaveHistoryResponseDataDTO(
            history_id=history_id,
        ),
    )

    assert dto.model_dump() == {
        "success": True,
        "message": "History saved successfully.",
        "data": {
            "history_id": history_id,
        },
    }
