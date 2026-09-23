import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import IssueActivityEventType
from app.models.issue import Issue
from app.models.issue_activity import IssueActivity
from app.services.authorization import is_project_member
from app.services.exceptions import AuthorizationError, NotFoundError

_FIELD_EVENTS: dict[str, IssueActivityEventType] = {
    "title": IssueActivityEventType.TITLE_CHANGED,
    "description": IssueActivityEventType.DESCRIPTION_CHANGED,
    "status": IssueActivityEventType.STATUS_CHANGED,
    "priority": IssueActivityEventType.PRIORITY_CHANGED,
    "assignee_id": IssueActivityEventType.ASSIGNEE_CHANGED,
}

# Fields whose actual values are safe and useful to record (short,
# structured). Fields left out of this set (currently: description) still
# get an activity entry, but without old/new content — see the module
# docstring on IssueActivity for why.
_VALUE_FIELDS = {"title", "status", "priority", "assignee_id"}


def _stringify(value: Any) -> str | None:
    return None if value is None else str(value)


def record_created(db: Session, issue: Issue, actor_id: uuid.UUID) -> None:
    db.add(IssueActivity(issue_id=issue.id, actor_id=actor_id, event_type=IssueActivityEventType.CREATED))


def record_updates(db: Session, issue: Issue, actor_id: uuid.UUID, updates: dict[str, Any]) -> None:
    """Diffs `updates` against `issue`'s current values and records one
    activity entry per field that actually changed. Must be called before
    the updates are applied to `issue`."""
    for field, new_value in updates.items():
        event_type = _FIELD_EVENTS.get(field)
        if event_type is None:
            continue

        old_value = getattr(issue, field)
        if old_value == new_value:
            continue

        if field in _VALUE_FIELDS:
            db.add(
                IssueActivity(
                    issue_id=issue.id,
                    actor_id=actor_id,
                    event_type=event_type,
                    field_name=field,
                    old_value=_stringify(old_value),
                    new_value=_stringify(new_value),
                )
            )
        else:
            db.add(
                IssueActivity(issue_id=issue.id, actor_id=actor_id, event_type=event_type, field_name=field)
            )


def list_activity(
    db: Session, issue_id: uuid.UUID, acting_user_id: uuid.UUID, limit: int = 100, offset: int = 0
) -> list[IssueActivity]:
    # Inlined rather than importing app.services.issues, to avoid a circular
    # import (issues.py calls record_created/record_updates in this module).
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise NotFoundError(f"Issue {issue_id} not found.")
    if not is_project_member(db, issue.project_id, acting_user_id):
        raise AuthorizationError(f"User {acting_user_id} is not a member of project {issue.project_id}.")

    stmt = (
        select(IssueActivity)
        .where(IssueActivity.issue_id == issue_id)
        .order_by(IssueActivity.created_at, IssueActivity.id)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))
