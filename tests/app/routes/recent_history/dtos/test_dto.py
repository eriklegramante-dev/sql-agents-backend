from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.routes.recent_history.dtos.dto import (
    RecentHistoryItemDTO,
    RecentHistoryResponseDTO,
)


def test_recent_history_item_accepts_valid_payload():
    history_id = uuid4()
    dataset_id = uuid4()
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    updated_at = datetime(2026, 1, 2, tzinfo=timezone.utc)

    dto = RecentHistoryItemDTO(
        id=history_id,
        dataset_id=dataset_id,
        title="Sales report",
        status="ACTIVE",
        created_at=created_at,
        updated_at=updated_at,
    )

    assert dto.id == history_id
    assert dto.dataset_id == dataset_id
    assert dto.title == "Sales report"
    assert dto.status == "ACTIVE"
    assert dto.created_at == created_at
    assert dto.updated_at == updated_at


def test_recent_history_item_accepts_null_dataset_id():
    dto = RecentHistoryItemDTO(
        id=uuid4(),
        dataset_id=None,
        title="Untitled",
        status="ARCHIVED",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    assert dto.dataset_id is None


def test_recent_history_item_rejects_invalid_id():
    with pytest.raises(ValidationError):
        RecentHistoryItemDTO(
            id="invalid",
            title="Sales report",
            status="ACTIVE",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        )


def test_recent_history_response_serializes_payload():
    item = RecentHistoryItemDTO(
        id=uuid4(),
        dataset_id=None,
        title="Sales report",
        status="ACTIVE",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    dto = RecentHistoryResponseDTO(
        success=True,
        message="ok",
        data=[item],
    )

    assert dto.success is True
    assert dto.message == "ok"
    assert dto.data == [item]


def test_recent_history_response_requires_data():
    with pytest.raises(ValidationError):
        RecentHistoryResponseDTO(success=True, message="ok")
