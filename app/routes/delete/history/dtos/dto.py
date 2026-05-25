from typing import Any, Optional

from pydantic import BaseModel, Field


class DeleteHistoryResponseDTO(BaseModel):
    """
    Response DTO for deleting the oldest chat history record.

    Attributes:
        success (bool): Indicates if the operation was successful.
        message (Optional[str]): Contextual message for the operation.
        data (Optional[Any]): Contains the deleted chat history information.
    """

    success: bool = Field(
        ...,
        description="Indicates if the operation was successful.",
    )

    message: Optional[str] = Field(
        None,
        description="Contextual message for the operation.",
    )

    data: Optional[Any] = Field(
        None,
        description="Contains the deleted oldest chat history information.",
    )
