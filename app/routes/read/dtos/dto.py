from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.users_table import (
    UserRole,
    UserStatus,
)


class GetUserRequestDTO(BaseModel):
    """
    DTO for user read requests with optional filters.
    """

    id: Optional[int] = Field(
        None,
        gt=0,
        description="Unique identifier of the user.",
    )

    email: Optional[EmailStr] = Field(
        None,
        description="User email address used as a search filter.",
    )

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User full name used as a search filter.",
    )

    cpf: Optional[str] = Field(
        None,
        min_length=11,
        max_length=14,
        pattern=r"^([0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})$",
        description="User CPF number used as a search filter.",
    )

    country: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-zÀ-ÿ\s]+$",
        description="User country used as a search filter.",
    )

    role: Optional[UserRole] = Field(
        None, description="User role used as a search filter."
    )

    status: Optional[UserStatus] = Field(
        None, description="User status used as a search filter."
    )

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_cpf = value.replace(".", "").replace("-", "")

        if not cleaned_cpf.isdigit():
            raise ValueError("CPF must contain only numeric characters.")

        if len(cleaned_cpf) != 11:
            raise ValueError("CPF must countain exactly 11 digits.")

        return cleaned_cpf

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        cleaned_country = value.strip()

        if not all(char.isalpha() or char.isspace() for char in cleaned_country):
            raise ValueError(
                "Country must contain only alphabetic characters and spaces."
            )

        return cleaned_country


class GetUserResponseDTO(BaseModel):
    """
    Standard response DTO for user read operations.
    """

    success: bool = Field(
        description="Indicates whether the read operation was successful."
    )

    message: Optional[str] = Field(
        None, description="Contextual message about the operation the operation result."
    )

    data: Optional[Any] = Field(None, description="Returned user data.")
