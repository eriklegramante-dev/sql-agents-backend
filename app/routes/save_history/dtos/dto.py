from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class SaveHistoryRequestDTO(BaseModel):
    """
    DTO used to create a new history record.
    """

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
