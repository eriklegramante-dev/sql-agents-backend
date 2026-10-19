import enum
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    func,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.models.users_table import Base

from sqlalchemy import JSON


class HistoryStatus(enum.Enum):
    """
    Available status values
    for history records.
    """

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class HistoryTable(Base):
    """
    Database model representing user history records.

    Records with a session identifier are unique per user and session.
    Legacy records may omit the session identifier.
    """

    __tablename__ = "history"
    __table_args__ = (
        UniqueConstraint("user_id", "session_id", name="uq_history_user_session"),
    )

    session_id = Column(UUID(as_uuid=True), nullable=True)

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    dataset_id = Column(
        UUID(as_uuid=True),
        nullable=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        JSON,
        nullable=False,
    )

    status = Column(
        Enum(HistoryStatus, name="historystatus"),
        nullable=False,
        default=HistoryStatus.ACTIVE,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
