import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.authorization import is_project_member
from app.services.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.services.projects import get_project_for_member


def create_issue(db: Session, project_id: uuid.UUID, creator: User, data: IssueCreate) -> Issue:
    get_project_for_member(db, project_id, creator.id)  # 404/403; only members may create issues

    if data.assignee_id is not None and not is_project_member(db, project_id, data.assignee_id):
        raise ValidationError(f"Assignee {data.assignee_id} must be a member of project {project_id}.")

    issue = Issue(
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assignee_id=data.assignee_id,
        created_by_id=creator.id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def get_issue(db: Session, issue_id: uuid.UUID) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise NotFoundError(f"Issue {issue_id} not found.")
    return issue


def get_issue_for_member(db: Session, issue_id: uuid.UUID, user_id: uuid.UUID) -> Issue:
    """Fetch an issue, requiring the caller to be a member of its project."""
    issue = get_issue(db, issue_id)
    if not is_project_member(db, issue.project_id, user_id):
        raise AuthorizationError(f"User {user_id} is not a member of project {issue.project_id}.")
    return issue


def list_project_issues(
    db: Session, project_id: uuid.UUID, acting_user_id: uuid.UUID, limit: int = 100, offset: int = 0
) -> list[Issue]:
    get_project_for_member(db, project_id, acting_user_id)  # 404/403
    stmt = (
        select(Issue)
        .where(Issue.project_id == project_id)
        .order_by(Issue.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def update_issue(db: Session, issue_id: uuid.UUID, acting_user_id: uuid.UUID, data: IssueUpdate) -> Issue:
    issue = get_issue_for_member(db, issue_id, acting_user_id)  # 404/403; only members may update
    updates = data.model_dump(exclude_unset=True)

    if updates.get("assignee_id") is not None and not is_project_member(
        db, issue.project_id, updates["assignee_id"]
    ):
        raise ValidationError(
            f"Assignee {updates['assignee_id']} must be a member of project {issue.project_id}."
        )

    for field, value in updates.items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue_id: uuid.UUID, acting_user_id: uuid.UUID) -> None:
    issue = get_issue_for_member(db, issue_id, acting_user_id)  # 404/403; only members may delete
    db.delete(issue)
    db.commit()
