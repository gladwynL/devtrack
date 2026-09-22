class NotFoundError(Exception):
    """Raised when a requested resource does not exist. Mapped to HTTP 404."""


class ConflictError(Exception):
    """Raised when an operation would violate a uniqueness constraint. Mapped to HTTP 409."""


class ValidationError(Exception):
    """Raised when a request violates a business rule. Mapped to HTTP 400."""


class AuthenticationError(Exception):
    """Raised when credentials or a token are missing or invalid. Mapped to HTTP 401."""


class AuthorizationError(Exception):
    """Raised when an authenticated user lacks permission for an action. Mapped to HTTP 403."""
