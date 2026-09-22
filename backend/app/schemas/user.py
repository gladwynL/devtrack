import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import validate_email


class UserBase(BaseModel):
    email: str = Field(max_length=255)
    display_name: str = Field(min_length=1, max_length=255)

    _validate_email = field_validator("email")(validate_email)


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)

    _validate_email = field_validator("email")(validate_email)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
