import re

from datetime import date
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUserRequestDTO(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Full name of the user."
    )
    email: EmailStr = Field(..., description="Email address of the user.")
    cpf: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="CPF with exactly 11 numeric digits (no dots or dashes).",
    )
    birth_date: date = Field(..., description="User's date of birth (YYYY-MM-DD).")
    country: str = Field(
        ..., min_length=2, max_length=50, description="Country of the user."
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description=(
            "User password. Must have at least 8 characters, contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special symbol (e.g., !@#$%)."
        ),
        example="MyStr0ngP@ssw0rd!",
    )

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("CPF must contain only digits.")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces.")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        today = date.today()
        if value > today:
            raise ValueError("Birth date cannot be in the future.")
        if (today.year - value.year) > 120:
            raise ValueError("Birth date is too far in the past (over 120 years ago).")
        return value

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Country cannot be empty or blank.")
        if not value.replace(" ", "").isalpha():
            raise ValueError(
                "Country must contain only alphabetic characters and spaces."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special symbol.")
        if " " in value:
            raise ValueError("Password cannot contain spaces.")
        return value


class CreateUserResponseDTO(BaseModel):
    success: bool = Field(..., description="Indicates if the operation was successful.")
    message: Optional[str] = Field(
        None, description="Contextual message for the operation."
    )
    data: Optional[Any] = Field(
        None, description="Resulting user object or related data."
    )
