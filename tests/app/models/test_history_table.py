from app.models.history_table import (
    HistoryTable,
    HistoryStatus,
)


def test_history_table_metadata_and_enums():
    assert HistoryTable.__tablename__ == "history"

    assert HistoryStatus.ACTIVE.value == "ACTIVE"
    assert HistoryStatus.ARCHIVED.value == "ARCHIVED"
    assert HistoryStatus.DELETED.value == "DELETED"
