from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class SaveHistoryRequestDTO(BaseModel):
    """
    DTO used to create history or update a saved user session.

    An optional session identifier selects atomic creation or update
    of the authenticated user's session. Omitting it creates a new
    legacy history record.
    """

    session_id: UUID | None = None

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="History title.",
    )

    message: dict[str, Any] = Field(
        ...,
        description="Chat payload.",
    )

    dataset_id: Optional[UUID] = Field(
        None,
        description="Optional dataset identifier.",
    )


class SaveHistoryResponseDataDTO(BaseModel):
    """
    Response payload containing
    history-specific data.
    """

    history_id: Optional[UUID] = Field(
        None,
        description="Created history identifier.",
    )


class SaveHistoryResponseDTO(BaseModel):
    """
    Standard response DTO for history creation.
    """

    success: bool = Field(...)

    message: str = Field(...)

    data: SaveHistoryResponseDataDTO = Field(...)
