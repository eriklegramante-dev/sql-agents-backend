from typing import Any, Optional

import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.users_table import UserRole, UserStatus


class UpdateUserRequestDTO(BaseModel):
    """
    DTO for user update requests.
    """

    id: Optional[int] = Field(None)
    email: Optional[EmailStr] = Field(None)

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    role: Optional[UserRole] = Field(None)
    status: Optional[UserStatus] = Field(None)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        if not value.isdigit():
            raise ValueError("CPF must contain only digits.")

        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Name must contain only alphabetic characters and spaces."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number."
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError( 
                "Password must contain at least one special symbol."
            )

        if " " in value:
            raise ValueError("Password cannot contain spaces.")

        return value


class UpdateUserResponseDTO(BaseModel):
    """
    Standard response DTO for update operations.
    """

    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None