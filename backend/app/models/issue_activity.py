import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.enums import IssueActivityEventType


def _utcnow() -> datetime:
    return datetime.now(UTC)


class IssueActivity(Base):
    """A lightweight, append-only log of notable changes to a single issue.

    This is intentionally scoped to issues only, not a generic app-wide audit
    system. Free-text fields (description) are recorded as "changed" without
    persisting their contents, to avoid storing large or sensitive text in
    the activity log.
    """

    __tablename__ = "issue_activities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # SET NULL rather than RESTRICT: this is a best-effort activity feed, not
    # a compliance audit log, so a deleted user's history entries are kept
    # (with actor_id null) rather than blocking their account deletion.
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[IssueActivityEventType] = mapped_column(
        SAEnum(
            IssueActivityEventType,
            name="issue_activity_event_type",
            native_enum=False,
            create_constraint=True,
            length=30,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    field_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    old_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )
