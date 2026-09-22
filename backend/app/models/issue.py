import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import IssuePriority, IssueStatus

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # native_enum=False keeps status/priority portable (VARCHAR + CHECK
    # constraint) across SQLite (tests) and Postgres (production).
    status: Mapped[IssueStatus] = mapped_column(
        SAEnum(
            IssueStatus,
            name="issue_status",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=IssueStatus.TODO,
        index=True,
    )
    priority: Mapped[IssuePriority] = mapped_column(
        SAEnum(
            IssuePriority,
            name="issue_priority",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=IssuePriority.MEDIUM,
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="issues")
    assignee: Mapped["User | None"] = relationship(
        back_populates="assigned_issues", foreign_keys=[assignee_id]
    )
    creator: Mapped["User"] = relationship(back_populates="created_issues", foreign_keys=[created_by_id])
