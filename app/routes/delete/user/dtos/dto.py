from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class DeleteUserRequestDTO(BaseModel):

    id: Optional[int] = Field(
        None,
        description="User ID used for deletion.",
    )

    email: Optional[EmailStr] = Field(
        None,
        description="User email used for deletion.",
    )

    cpf: Optional[str] = Field(
        None,
        min_length=11,
        max_length=11,
        description="CPF with exactly 11 numeric digits.",
    )

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: Optional[str]) -> Optional[str]:

        if value is not None and not value.isdigit():
            raise ValueError("CPF must contain only digits.")

        return value


class DeleteUserResponseDTO(BaseModel):

    success: bool = Field(
        ...,
        description="Indicates if the operation was successful.",
    )

    message: Optional[str] = Field(
        None,
        description="Contextual message for the operation.",
    )

    deleted_user_id: Optional[int] = Field(
        None,
        description="Deleted user ID.",
    )