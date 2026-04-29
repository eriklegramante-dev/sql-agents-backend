from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequestDTO(BaseModel):
    username: EmailStr = Field(
        ...,
        description="User email address. Example: user@example.com",
        min_length=5,
        max_length=128,
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password. Example: MyStr0ngP@ssw0rd!",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if " " in value:
            raise ValueError("Password cannot contain spaces.")
        return value


class LoginResponseDTO(BaseModel):
    success: bool = Field(..., description="Indicates if the login was successful.")
    message: Optional[str] = Field(None, description="Contextual message.")
    access_token: Optional[str] = Field(None, description="JWT access token.")
    token_type: Optional[str] = Field(None, description="Token type, usually 'bearer'.")
