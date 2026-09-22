import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.exceptions import NotFoundError, ValidationError
from app.services.memberships import is_project_member
from app.services.projects import get_project


def create_issue(db: Session, project_id: uuid.UUID, data: IssueCreate) -> Issue:
    get_project(db, project_id)  # 404 if the project does not exist

    if not is_project_member(db, project_id, data.created_by_id):
        raise ValidationError(
            f"User {data.created_by_id} must be a member of project {project_id} to create issues."
        )
    if data.assignee_id is not None and not is_project_member(db, project_id, data.assignee_id):
        raise ValidationError(f"Assignee {data.assignee_id} must be a member of project {project_id}.")

    issue = Issue(
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        assignee_id=data.assignee_id,
        created_by_id=data.created_by_id,
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


def list_project_issues(db: Session, project_id: uuid.UUID, limit: int = 100, offset: int = 0) -> list[Issue]:
    get_project(db, project_id)  # 404 if the project does not exist
    stmt = (
        select(Issue)
        .where(Issue.project_id == project_id)
        .order_by(Issue.created_at)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))


def update_issue(db: Session, issue_id: uuid.UUID, data: IssueUpdate) -> Issue:
    issue = get_issue(db, issue_id)
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


def delete_issue(db: Session, issue_id: uuid.UUID) -> None:
    issue = get_issue(db, issue_id)
    db.delete(issue)
    db.commit()
