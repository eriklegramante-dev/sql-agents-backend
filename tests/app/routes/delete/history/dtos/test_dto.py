import pytest
from pydantic import ValidationError

from app.routes.delete.history.dtos.dto import DeleteHistoryResponseDTO


def test_delete_history_response_success_with_deleted_history_id():
    dto = DeleteHistoryResponseDTO(
        success=True,
        message="Chat history deleted successfully.",
        data={"deleted_history_id": 1},
    )

    assert dto.success is True
    assert dto.message == "Chat history deleted successfully."
    assert dto.data["deleted_history_id"] == 1


def test_delete_history_response_failure_without_deleted_history_id():
    dto = DeleteHistoryResponseDTO(
        success=False,
        message="Chat history not found.",
    )

    assert dto.success is False
    assert dto.message == "Chat history not found."
    assert dto.data is None


def test_delete_history_response_accepts_empty_data_dict():
    dto = DeleteHistoryResponseDTO(
        success=True,
        message="Chat history deleted successfully.",
        data={},
    )

    assert dto.success is True
    assert dto.message == "Chat history deleted successfully."
    assert dto.data == {}


def test_delete_history_response_accepts_none_message():
    dto = DeleteHistoryResponseDTO(
        success=True,
        data={"deleted_history_id": 1},
    )

    assert dto.success is True
    assert dto.message is None
    assert dto.data["deleted_history_id"] == 1


def test_delete_history_response_requires_success():
    with pytest.raises(ValidationError):
        DeleteHistoryResponseDTO()
