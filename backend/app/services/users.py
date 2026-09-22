import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.exceptions import ConflictError, NotFoundError


def create_user(db: Session, data: UserCreate) -> User:
    user = User(email=data.email, display_name=data.display_name)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"A user with email '{data.email}' already exists.") from exc
    db.refresh(user)
    return user


def get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found.")
    return user


def list_users(db: Session, limit: int = 100, offset: int = 0) -> list[User]:
    stmt = select(User).order_by(User.created_at).limit(limit).offset(offset)
    return list(db.scalars(stmt))


def update_user(db: Session, user_id: uuid.UUID, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(f"A user with email '{data.email}' already exists.") from exc
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: uuid.UUID) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            f"User {user_id} cannot be deleted while they still own a project or created an issue."
        ) from exc
