import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(value: str | None) -> str | None:
    if value is not None and not _EMAIL_PATTERN.match(value):
        raise ValueError("must be a valid email address")
    return value
