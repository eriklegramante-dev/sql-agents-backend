from pydantic import BaseModel, Field


class ChatSessionCountDataDTO(BaseModel):
    """
    Response payload containing the authenticated user's session total.

    The total is a non-negative count of active and archived histories
    with a session identifier, excluding deleted and legacy records.
    """

    total: int = Field(
        ...,
        ge=0,
        description="Number of saved sessions excluding deleted histories.",
    )


class ChatSessionCountResponseDTO(BaseModel):
    """
    Standard response DTO for saved conversation session counting.

    Contains the operation status, message, and session count payload.
    The data field is None when the operation fails.
    """

    success: bool
    message: str
    data: ChatSessionCountDataDTO | None