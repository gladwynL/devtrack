import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str | None) -> str | None:
    if value is not None and not _EMAIL_PATTERN.match(value):
        raise ValueError("must be a valid email address")
    return value


class UserBase(BaseModel):
    email: str = Field(max_length=255)
    display_name: str = Field(min_length=1, max_length=255)

    _validate_email = field_validator("email")(_validate_email)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, max_length=255)
    display_name: str | None = Field(default=None, min_length=1, max_length=255)

    _validate_email = field_validator("email")(_validate_email)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
