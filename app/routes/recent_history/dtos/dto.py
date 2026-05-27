from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RecentHistoryItemDTO(BaseModel):
    """
    DTO representing a single recent history entry.
    """

    id: UUID = Field(
        ...,
        description="Unique identifier of the history entry.",
    )

    dataset_id: Optional[UUID] = Field(
        None,
        description="Optional related dataset identifier.",
    )

    title: str = Field(
        ...,
        description="Conversation title displayed in the recent history list.",
    )

    status: str = Field(
        ...,
        description="Current status of the history entry.",
    )

    created_at: datetime = Field(
        ...,
        description="Timestamp when the history entry was created.",
    )

    updated_at: datetime = Field(
        ...,
        description="Timestamp when the history entry was last updated.",
    )


class RecentHistoryResponseDTO(BaseModel):
    """
    Standard response DTO for recent history retrieval operations.
    """

    model_config = ConfigDict(from_attributes=True)
    success: bool = Field(
        ...,
        description="Indicates whether the retrieval operation was successful.",
    )

    message: Optional[str] = Field(
        None,
        description="Optional message providing additional information about the operation.",
    )

    data: list[RecentHistoryItemDTO] = Field(
        ...,
        description="List containing the user's most recent history entries.",
    )
