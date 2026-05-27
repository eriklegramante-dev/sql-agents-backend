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
)
from sqlalchemy.dialects.postgresql import UUID

from app.models.users_table import Base


class HistoryStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


class HistoryTable(Base):
    __tablename__ = "history"

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
