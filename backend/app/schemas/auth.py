from pydantic import BaseModel, Field, field_validator

from app.schemas.user import UserBase
from app.schemas.validators import validate_email


class RegisterRequest(UserBase):
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=1, max_length=128)

    _validate_email = field_validator("email")(validate_email)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
