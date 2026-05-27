from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func

from app.models.users_table import Base


class ChatHistoryTable(Base):
    """
    Database model representing a chat history record.

    Attributes:
        id (Column): Primary key of the chat history record.
        user_id (Column): Identifier of the user who owns the history record.
        message (Column): Stored chat history content.
        created_at (Column): Timestamp when the record was created.
        updated_at (Column): Timestamp when the record was last updated.
    """

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
