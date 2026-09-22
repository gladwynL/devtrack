class NotFoundError(Exception):
    """Raised when a requested resource does not exist. Mapped to HTTP 404."""


class ConflictError(Exception):
    """Raised when an operation would violate a uniqueness constraint. Mapped to HTTP 409."""


class ValidationError(Exception):
    """Raised when a request violates a business rule. Mapped to HTTP 400."""
