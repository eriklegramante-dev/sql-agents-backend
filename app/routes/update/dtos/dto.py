from typing import Any, Optional

import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.users_table import UserRole, UserStatus


class UpdateUserRequestDTO(BaseModel):
    """
    DTO for user update requests with optional fields
    to support partial updates.
    """

    id: Optional[int] = Field(
        None,
        description="Unique identifier of the user to update. Required if email is not provided.",
    )

    email: Optional[EmailStr] = Field(
        None,
        description="Email address of the user to update. Required if id is not provided.",
    )

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Full name of the user. Optional but must be valid if provided.",
    )

    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="New password for the user. Optional but must meet complexity requirements if provided.",
    )

    role: Optional[UserRole] = Field(
        None,
        description="Role to assign to the user. Optional but must be a valid role if provided.",
    )

    status: Optional[UserStatus] = Field(
        None,
        description="Status to assign to the user. Optional but must be a valid status if provided.",
    )

    @model_validator(mode="after")
    def validate_update_request(self):
        """
        Validate request identifiers and mutable update fields.

        Ensures that the request contains at least one identifier
        to locate the target user and at least one mutable field
        to perform the update operation.

        Returns:
            UpdateUserRequestDTO:
                The validated DTO instance.

        Raises:
            ValueError:
                Raised when no identifier or update field is provided.
        """

        has_identifier = any(
            [
                self.id,
                self.email,
            ]
        )

        if not has_identifier:
            raise ValueError("At least one identifier is required.")

        has_update_fields = any(
            [
                self.name,
                self.email,
                self.password,
                self.role,
                self.status,
            ]
        )

        if not has_update_fields:
            raise ValueError("No update fields were provided.")

        return self

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional names when they are included in update payloads."""
        if value is None:
            return value

        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces.")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional passwords against the service complexity policy."""
        if value is None:
            return value

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


class UpdateUserResponseDTO(BaseModel):
    """
    Standard response DTO for update operations.
    """

    success: bool = Field(
        ..., description="Indicates whether the update operation was successful."
    )
    message: Optional[str] = Field(
        None,
        description="Optional message providing additional information about the update operation.",
    )
    data: Optional[Any] = Field(
        None, description="Optional data containing the updated user information."
    )
