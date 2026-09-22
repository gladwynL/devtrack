from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.exceptions import AuthenticationError, ConflictError


def register_user(db: Session, data: RegisterRequest) -> User:
    user = User(
        email=data.email,
        display_name=data.display_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"A user with email '{data.email}' already exists.") from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: LoginRequest) -> User:
    user = db.scalar(select(User).where(User.email == data.email))
    # Same error for an unknown email and a wrong password, so the response
    # never reveals whether an account exists for that address.
    if user is None or not verify_password(data.password, user.password_hash):
        raise AuthenticationError("Incorrect email or password.")
    return user


def issue_access_token(user: User) -> str:
    return create_access_token(subject=user.id)
